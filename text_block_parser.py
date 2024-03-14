import re

# """
#
#     'Synonyms' command - {variant1 | variant2 | variant3} - insert one of the variants to the result string
#     If you want to omit text - use 'empty' variant - {|variant}
#     Mixin command = [ text 1 | text 2 | text 3] - will mix this variants randomly
#     You can use separator in mixin - [+,+text 1|text2 ] - you will get text2,text1.
#     Separator can by any symbol or set of symbols: [+==+ a|b] - a==b or b==a
#     If you want to get spesial symbol in your result ('{', '}', '[', ']', '|', '+') - use backslash for it - {, }, [, ], |, +
#     All this commands can be mixed and nested in all combinations: 'start {aa|bb|{cc1|cc2}} or [a1|{word1|word2}|a3| [aa1|aa2|aa3]]'
#     You can use special predefined random functions in templates
#     - {random integer = $RANDINT(1,10), uuid = $UUID, now = $NOW(%Y-%M-%d)}.
#     Result will be = 'random integer = 4, uuid = 8ae6bdf4-d321-40f6-8c3c-81d20b158acb, now = 2017-08-01'
#     You can define your own randomization functions and use it in templates. Read about functions further.
#
# """


text = """Он {$$Bolock1Name$$}, {$$Bock2Name$$}.
Цвет кожи:
    """

# принимает текст выдает список строк (разделитель перевод строки \n)
def get_strings_from_text(text: str) -> list[str]:
    return [i for i in text.split("\n")]


def main():


    list_string = get_strings_from_text(text)

    for sring in list_string:
        print(sring)





if (__name__ == '__main__'):
    main()
