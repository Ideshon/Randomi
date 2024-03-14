from re import sub  # стандартная библиотека для работы с текстом

from text_randomizer import TextRandomizer  # хуита с github


class TextBlock:  # обьявляем класс

    # конструктор класса
    # сдесь создаются индивидуальные поля(переменные) обьекта
    # при создании обьекта нужно передать ему аргументы(они в скобках)
    def __init__(
            self,
            text_before: str = "",
            text_template: str = "",
            template_delimeter: str = ",",
            text_after: str = "",
            action: str = "rand"  # "rand" "shuffle" "origin"
            ):

        self.template_delimeter = template_delimeter
        self.template = text_template
        self.out_text = ""
        self.text_before = text_before
        self.text_after = text_after

        self.action = action


    # функция нормализации примера (для , ->  1,2,3 в {1|2|3})
    def normalize_template(self, action):
        norm_template = sub(f"{self.template_delimeter}", "|", self.template)
        if (action == "rand"):
            norm_template = "{" + f"{norm_template}" + "}"
        elif (action == "shuffle"):
            norm_template = "[" + f"{norm_template}" + "]"
        return norm_template


    # функция которая возвращает рандоминизированный текст
    def __get_randomize_text__(self, action) -> str:
        norm_template = self.normalize_template(action)
        text_rnd = TextRandomizer(norm_template).get_text()
        return str(text_rnd)


    # функция генерации выходного текста
    def __gen_text__(self):
        if ((self.action == "rand") or (self.action == "shuffle")):
            text_rnd = self.__get_randomize_text__(self.action)
            self.out_text = self.text_before + text_rnd + self.text_after

        elif (self.action == "origin"):
            self.out_text = self.text_before + self.template + self.text_after

        else:
            self.out_text = "Error action"


    # -------------------------------------------
    # если нужно обновить значения блока после создания

    def set_before_text(self, text):
        if (not (text is None)):
            self.text_before = text


    def set_after_text(self, text: str):
        if (not (text is None)):
            self.text_after = text


    def set_template_text(self, text: str):
        if (not (text is None)):
            self.template = text


    def set_template_delimeter(self, text: str):
        if (not (text is None)):
            self.template_delimeter = text


    def set_action(self, action: str):
        self.action = action


    # -------------------------------------------

    # генерирует и возвращает выходной текст
    def get_out_text(self):
        self.__gen_text__()
        return self.out_text


def main():
    before = "Before"
    template = "Template,Template2,Template3,Template4,Template5"
    after = "After"

    # создаем обьект класса
    block = TextBlock(text_before=before, text_template=template, text_after=after, action="rand")

    # выводим 5 генераций обьекта
    for i in range(5):
        print(block.get_out_text())

    # новые данные

    template2 = "Template6,Template7,Template8,Template9,Template10"
    before2 = "Before2"
    after2 = "After2"

    # меняем значения в классе

    block.set_before_text(before2)
    block.set_after_text(after2)
    block.set_template_text(template2)

    print("-" * 60)  # линия

    for i in range(5):
        print(block.get_out_text())

    block.set_action("shuffle")  # перемешивание

    print("-" * 60)

    for i in range(5):
        print(block.get_out_text())

    block.set_action("origin")  # оригинал

    print("-" * 60)

    for i in range(5):
        print(block.get_out_text())

# штука
if (__name__ == '__main__'):
    main()
