"""
Этот модуль "дополняет" наш идеальный text_randomizer.py
новыми функциями или переопределением, не изменяя исходный text_randomizer.py.

Здесь мы делаем класс TextRandomizer, который наследует
уже существующий класс TextRandomizer из text_randomizer.py,
и при необходимости добавляем/переопределяем методы.
"""

from text_randomizer import TextRandomizer as BaseTextRandomizer


class TextRandomizer(BaseTextRandomizer):
    """
    Наследуемся от "идеального" TextRandomizer
    и добавляем (или переопределяем) некоторые возможности.
    """

    def __init__(self, template, delimiter='|', func_delimiter=','):
        # Вызываем конструктор базового класса
        super().__init__(template, delimiter, func_delimiter)

    # Пример новой/дополнительной функции:
    # $MYFUNC(arg1, arg2, ...)
    # Вы можете добавить её в _process_functions() через override
    # или задать здесь отдельный метод, а в _process_functions() проверять на MYFUNC.
    #
    # Ниже, для примера, переопределим _process_functions() и
    # добавим поддержку $MYFUNC(...). Если не нужно — удалите этот пример.
    #
    def _process_functions(self, text):
        """
        Переопределяем, чтобы добавить логику для $MYFUNC(...)
        и вызывать логику из родителя для остальных случаев.
        """
        def evaluate_functions(s):
            # Локальная копия родительской логики
            # (с небольшими изменениями для добавления MYFUNC).
            result = ''
            i = 0

            while i < len(s):
                if s[i] == '$':
                    func_start = i
                    i += 1
                    func_name = ''

                    # Читаем имя функции
                    while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                        func_name += s[i]
                        i += 1

                    # Ожидаем '('
                    if i >= len(s) or s[i] != '(':
                        # Не похоже на функцию, возвращаем как есть
                        result += s[func_start:i]
                        continue

                    i += 1  # пропускаем '('
                    args = []
                    current_arg = ''
                    depth = 1

                    # Собираем аргументы
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
                        raise ValueError("Unbalanced parentheses in function call")

                    # Рекурсивная обработка аргументов
                    evaluated_args = [evaluate_functions(arg) for arg in args]

                    # Смотрим, какая функция
                    upper_name = func_name.upper()
                    if upper_name == 'MYFUNC':
                        # Вызов вашей новой функции
                        result += self._replace_myfunc(*evaluated_args)
                    else:
                        # Если не MYFUNC — вызываем родительский вариант (из "идеального" TextRandomizer)
                        # Для этого применим базовый метод прямо к исходному фрагменту:
                        # Соберём строку заново и передадим в базовый _process_functions()
                        original_str = f"${func_name}({','.join(evaluated_args)})"
                        # Запустим базовый метод:
                        # (можно re-inject через родительский process_functions, но аккуратно)
                        replaced = super()._process_functions(original_str)
                        result += replaced

                else:
                    result += s[i]
                    i += 1

            return result

        return evaluate_functions(text)

    def _replace_myfunc(self, *args):
        """
        Пример новой функции MYFUNC(...).
        Здесь вы делаете что угодно с аргументами и возвращаете строку.
        """
        # Допустим, просто вернём все аргументы, склеенные через ' + '
        return ' + '.join(args)
