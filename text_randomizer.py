import re
import random

class TextRandomizer:
    def __init__(self, template, delimiter='|', func_delimiter=','):
        self.template = template
        self.delimiter = delimiter
        self.func_delimiter = func_delimiter

    def process(self):
        parts = re.split('(<[^>]+>)', self.template)
        new_parts = []
        for part in parts:
            if part.startswith('<'):
                new_parts.append(part)
            else:
                part = self._process_delimiters(part)
                part = self._process_functions(part)
                new_parts.append(part)
        return ''.join(new_parts)

    def _process_delimiters(self, text):
        if self.delimiter and self.delimiter != '|':
            escaped_delim = re.escape(self.delimiter)
            text = re.sub(rf'\s*{escaped_delim}\s*', '|', text)
        return text

    def _process_functions(self, text):
        def evaluate_functions(s):
            result = ''
            i = 0

            while i < len(s):
                if s[i] == '$':
                    func_start = i
                    i += 1
                    func_name = ''
                    # Извлекаем имя функции
                    while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                        func_name += s[i]
                        i += 1
                    if i >= len(s) or s[i] != '(':
                        result += s[func_start:i]
                        continue
                    i += 1  # Пропускаем '('

                    args = []
                    current_arg = ''
                    depth = 1

                    # Разбираем аргументы функции
                    while i < len(s) and depth > 0:
                        if s[i] == '(':
                            depth += 1
                            current_arg += s[i]
                        elif s[i] == ')':
                            depth -= 1
                            if depth == 0:
                                args.append(current_arg.strip())
                                break
                            else:
                                current_arg += s[i]
                        elif s[i] == ',' and depth == 1:
                            args.append(current_arg.strip())
                            current_arg = ''
                        else:
                            current_arg += s[i]
                        i += 1

                    if depth != 0:
                        raise ValueError(f"Unbalanced parenthesis in function starting at position {func_start}")

                    # Рекурсивно обрабатываем аргументы (сначала внутренние функции)
                    evaluated_args = [evaluate_functions(arg) for arg in args]

                    # Вызываем соответствующую функцию
                    if func_name == 'MULTIPLY':
                        result += self._replace_multiply_function(*evaluated_args)
                    elif func_name == 'RANDWORDS':
                        result += self._replace_randwords_function(*evaluated_args)
                    else:
                        result += f"${func_name}({','.join(evaluated_args)})"
                else:
                    result += s[i]
                    i += 1

            return result

        return evaluate_functions(text)

    def _replace_multiply_function(self, word, count):
        try:
            count = int(count)
            return ' '.join([word] * count)
        except ValueError:
            raise ValueError(f"Invalid count value for MULTIPLY: {count}")

    def _replace_randwords_function(self, min_count, max_count, *words):
        try:
            min_count = int(min_count)
            max_count = int(max_count)
            words = [word.strip() for word in words]
            if not words:
                return ''
            max_count = min(max_count, len(words))
            min_count = min(min_count, max_count)
            if max_count <= 0:
                return ''
            num_words = random.randint(min_count, max_count)
            selected_words = random.sample(words, num_words)
            return ' '.join(selected_words)
        except ValueError:
            raise ValueError(f"Invalid range values for RANDWORDS: min={min_count}, max={max_count}")
