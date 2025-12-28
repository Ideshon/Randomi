import re
import random
import html as html_lib

from .errors import TemplateError
from .logging_setup import log


class TemplateProcessor:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def process_html(
        self,
        entry_html: str,
        entry_plain: str,
        *,
        delimiter: str,
        func_delimiter: str,
    ) -> str:
        """
        Обрабатываем HTML из QTextEdit:
        - сохраняем теги,
        - работаем с текстовыми узлами в plain-виде,
        - вычисляем $MULTIPLY и $RANDWORDS до передачи в TextRandomizer,
        - при ошибках кидаем TemplateError с координатами по entry_plain.
        """
        parts = re.split(r'(<[^>]+>)', entry_html)
        new_parts: list[str] = []

        plain_pos = 0  # позиция в entry_plain, которую “потребили”

        def consume_newline_if_present():
            nonlocal plain_pos
            if plain_pos < len(entry_plain) and entry_plain[plain_pos] == "\n":
                plain_pos += 1

        for part in parts:
            if part.startswith("<"):
                # теги оставляем как есть
                new_parts.append(part)

                tag = part.lower()
                # Qt обычно превращает переносы в <br> и границы абзацев в </p> с \n в toPlainText()
                if tag.startswith("<br"):
                    consume_newline_if_present()
                elif tag.startswith("</p"):
                    consume_newline_if_present()

                continue

            # текстовый кусок
            plain_chunk = html_lib.unescape(part).replace("\u00a0", " ")
            if plain_chunk.strip() == "":
                # почти всегда это мусорные переносы/пробелы из форматирования HTML
                new_parts.append(part)
                continue

            # пробуем синхронизироваться с entry_plain
            base_offset = None

            if plain_pos <= len(entry_plain):
                if entry_plain.startswith(plain_chunk, plain_pos):
                    base_offset = plain_pos
                    plain_pos += len(plain_chunk)
                else:
                    idx = entry_plain.find(plain_chunk, plain_pos)
                    if idx != -1:
                        base_offset = idx
                        plain_pos = idx + len(plain_chunk)
                    else:
                        # ну не нашли, бывает (Qt иногда нормализует пробелы странно)
                        base_offset = plain_pos
                        plain_pos = min(len(entry_plain), plain_pos + len(plain_chunk))

            processed = plain_chunk

            # delimiter: заменяем пользовательский разделитель на '|'
            if delimiter and delimiter != "|":
                escaped_delim = re.escape(delimiter)
                processed = re.sub(rf"\s*{escaped_delim}\s*", "|", processed)

            # word*3 -> {$MULTIPLY(word,count)}
            processed = re.sub(
                r"(\w+)\*(\d+)",
                lambda m: "{$" + f"MULTIPLY({m.group(1)},{m.group(2)})" + "}",
                processed
            )

            # %1-2(a,b,c) -> {$RANDWORDS(1,2,a,b,c)} (с func_delimiter)
            def replace_randwords(match):
                min_count = match.group(1)
                max_count = match.group(2)
                words = match.group(3)
                return "{$RANDWORDS(" + f"{min_count}{func_delimiter}{max_count}{func_delimiter}{words}" + ")}"

            processed = re.sub(r"%(\d+)-(\d+)\((.*?)\)", replace_randwords, processed)

            # вычисляем $MULTIPLY и $RANDWORDS
            processed = self.evaluate_functions_in_text(
                processed,
                func_delimiter=func_delimiter,
                full_text=entry_plain,
                base_offset=base_offset,
            )

            # обратно в HTML-текстовый узел
            new_parts.append(html_lib.escape(processed, quote=False))

        return "".join(new_parts)

    def evaluate_functions_in_text(
        self,
        text: str,
        *,
        func_delimiter: str,
        full_text: str | None,
        base_offset: int | None,
    ) -> str:
        log.debug("evaluate_functions_in_text: len=%d func_delimiter=%r base_offset=%r",
                  len(text), func_delimiter, base_offset)

        def make_error(msg: str, local_pos: int, inner=None):
            if full_text is not None and base_offset is not None:
                full_pos = base_offset + local_pos
                ft = full_text
            else:
                full_pos = None
                ft = None

            raise TemplateError(
                msg,
                text,
                local_pos,
                inner=inner,
                full_text=ft,
                full_pos=full_pos,
            )

        def parse_function(s: str, start: int):
            func_name = ""
            i = start
            while i < len(s) and (s[i].isalnum() or s[i] == "_"):
                func_name += s[i]
                i += 1
            if i >= len(s) or s[i] != "(":
                return None, start

            i += 1  # skip '('
            args = []
            arg = ""
            depth = 1

            while i < len(s) and depth > 0:
                if depth == 1 and s[i:i + len(func_delimiter)] == func_delimiter:
                    args.append(arg)
                    arg = ""
                    i += len(func_delimiter)
                elif s[i] == "(":
                    depth += 1
                    arg += s[i]
                    i += 1
                elif s[i] == ")":
                    depth -= 1
                    if depth == 0:
                        args.append(arg)
                        i += 1
                        break
                    arg += s[i]
                    i += 1
                else:
                    arg += s[i]
                    i += 1

            if depth > 0:
                make_error(f"Несовпадающая скобка в вызове функции {func_name}", start - 1)

            return {"name": func_name, "args": args}, i

        def evaluate(s: str) -> str:
            result = ""
            i = 0
            while i < len(s):
                if s[i] != "$":
                    result += s[i]
                    i += 1
                    continue

                func_info, new_i = parse_function(s, i + 1)
                if not func_info:
                    result += s[i]
                    i += 1
                    continue

                # рекурсивно разворачиваем аргументы
                try:
                    evaluated_args = [evaluate(arg) for arg in func_info["args"]]
                except TemplateError as inner_te:
                    make_error(inner_te.user_message, i, inner=inner_te)

                try:
                    if func_info["name"] == "MULTIPLY":
                        res = self.multiply(*evaluated_args)
                    elif func_info["name"] == "RANDWORDS":
                        res = self.randwords(*evaluated_args)
                    else:
                        make_error(f"Неизвестная функция {func_info['name']}", i)
                except TypeError as e:
                    make_error("отсутствует необходимый элемент в функции", i, inner=e)
                except ValueError as e:
                    make_error("некорректное значение параметра в функции", i, inner=e)

                result += res
                i = new_i

            return result

        return evaluate(text)

    def multiply(self, word: str, count: str) -> str:
        if str(count).strip() == "":
            raise ValueError("параметр count пустой")
        return " ".join([word] * int(count))

    def randwords(self, min_count: str, max_count: str, *words: str) -> str:
        if str(min_count).strip() == "" or str(max_count).strip() == "":
            raise ValueError("минимум/максимум пустые")

        mn = int(min_count)
        mx = int(max_count)
        cleaned = [w.strip() for w in words if w.strip() != ""]

        mx = min(mx, len(cleaned))
        mn = min(mn, mx)

        if mx <= 0:
            return ""

        n = self.rng.randint(mn, mx)
        selected = self.rng.sample(cleaned, n)
        return " ".join(selected)
