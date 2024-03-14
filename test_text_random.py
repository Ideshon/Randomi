from text_randomizer import TextRandomizer
from text_block_parser import get_strings_from_text, text


def get_randomize_text(template):
    text_rnd = TextRandomizer(template)
    return text_rnd


def main():
    # get_randomize_text()

    list_strings = get_strings_from_text(text)

    for string in list_strings:
        print(TextRandomizer(string).get_text())


if (__name__ == '__main__'):
    main()
