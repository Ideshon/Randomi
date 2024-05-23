import random
import re
from text_randomizer import TextRandomizer

def expand_word_weight(input_text):
    print("Expanding word weight")
    pattern = r'%(\d+)\(([^()]*)\)'
    while True:
        match = re.findall(pattern, input_text)
        if not match:
            break
        for weight, words in match:
            words_list = words.split(';')
            if not words_list:
                continue
            total_words = sum(int(weight) for weight in words_list)
            selected_word = random.choices(words_list, weights=[int(weight) for weight in words_list], k=1)[0]
            input_text = input_text.replace(f'%{weight}({words})', selected_word, 1)
    print(f"Expanded text: {input_text}")
    return input_text

def expand_random_count(text):
    def process_nested_functions(text):
        nested_pattern = r'"(.*?)"'
        while re.findall(nested_pattern, text):
            for nested_formula in re.findall(nested_pattern, text):
                expanded_nested = expand_random_count(nested_formula)
                text = text.replace(f'"{nested_formula}"', expanded_nested, 1)
        return text

    text = process_nested_functions(text)

    pattern = r'%(\d+)-(\d+)\((.*?)\)'
    while True:
        match = re.findall(pattern, text)
        if not match:
            break
        for (min_count, max_count, words) in match:
            words_list = words.split(';')
            min_count, max_count = int(min_count), int(max_count)

            if min_count > len(words_list):
                min_count = len(words_list)
            if max_count > len(words_list):
                max_count = len(words_list)

            if min_count > max_count:
                min_count = max_count

            if not words_list:
                selected_words = ''
            else:
                num_words = random.randint(min_count, max_count)
                selected_words = ','.join(random.sample(words_list, num_words))

            formula = f'%{min_count}-{max_count}({words})'
            text = text.replace(formula, selected_words, 1)
    return text

def normalize_template(template, delimiter):
    print("Normalizing template")
    pattern = r'([^;]*%[^;]*)'
    matches = re.findall(pattern, template)
    if matches:
        result = delimiter.join(matches)
        print(f"Normalized result: {result}")
        return result
    print(f"Original template (no changes): {template}")
    return template

def randomize_text(template, delimiter, expand_word_weight, expand_random_count):
    try:
        print("Starting randomize_text")
        print(f"Template: {template}")

        expanded_template = expand_word_weight(template)
        print(f"Expanded template: {expanded_template}")

        expanded_template = expand_random_count(expanded_template)
        print(f"Expanded random count: {expanded_template}")

        norm_template = normalize_template(expanded_template, delimiter)
        print(f"Normalized template: {norm_template}")

        text_rnd = TextRandomizer(norm_template)
        randomized_text = text_rnd.get_text()
        print(f"Randomized text: {randomized_text}")

        cleaned_text = re.sub(r'(?<!\S),\s*', '', randomized_text)
        cleaned_text = re.sub(r'\s*,\s*,+', ',', cleaned_text)
        cleaned_text = re.sub(r'\(\s*,\s*', '(', cleaned_text)
        cleaned_text = re.sub(r'\s*,\s*\)', ')', cleaned_text)
        cleaned_text = re.sub(r'\s*,\s*', ', ', cleaned_text)
        cleaned_text = re.sub(r'[ \t]+(?=[^\S\n]*[ \t]+)', '', cleaned_text)
        cleaned_text = re.sub(r'[ \t]+(?=\n)', '', cleaned_text)
        cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
        cleaned_text = re.sub(r'^\s*,\s*', '', cleaned_text)

        print(f"Cleaned text: {cleaned_text}")
        return cleaned_text
    except Exception as e:
        return f"Error: {str(e)}"

# штука
if (__name__ == '__main__'):
    main()