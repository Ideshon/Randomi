import random


class TextRandomizer:
    def __init__(self, content):
        self.content = content

    def get_text(self):
        # Логика обработки текста
        return self.randomize_content(self.content)

    def randomize_content(self, content):
        # Пример обработки текста
        parts = content.split('|')
        return random.choice(parts)

    def multiply(self, word, count):
        return ' '.join([word] * int(count))

    def randwords(self, min_count, max_count, *words):
        min_count = int(min_count)
        max_count = int(max_count)
        words = [w.strip() for w in words]
        max_count = min(max_count, len(words))
        min_count = min(min_count, max_count)
        if max_count <= 0:
            return ''
        num_words = random.randint(min_count, max_count)
        selected_words = random.sample(words, num_words)
        return ' '.join(selected_words)
