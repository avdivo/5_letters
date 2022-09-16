import re
import sys, os

# Чтение слов
input_file = os.path.join(sys.path[0], 'five_letters_singular.txt')  # Файл ввода

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()
all_words = set(map(lambda x: x.rstrip(), all_words))  # Убираем дубликаты слов и перевод строки из них

a = ord('а')
alphabet = ''.join([chr(i) for i in range(a,a+6)] + [chr(a+33)] + [chr(i) for i in range(a+6,a+32)])

cou = 0
for pos in range(5):
    group_name = '.....'
    for letter in alphabet:
        group_name = group_name[:pos] + letter + '.' * (4 - pos)
        print('\n', group_name, '\n')
        for word in all_words:
            # Выводим слова, в которых заданная буква в ужной позиции
            if re.findall(group_name, word):
                cou += 1
                print(cou, word)
