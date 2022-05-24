# Читаем файл со всеми русскими словами и сохраняем файл с 5 буквенными словами
import sys, os


input_file = os.path.join(sys.path[0], 'all_words.txt')  # Файл ввода
output_file = os.path.join(sys.path[0], 'five_letters_words.txt')  # Файл вывода

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()

words_count = 0
with open(output_file, 'w', encoding='utf-8') as f:
    for word in all_words:
        word = word.rstrip()
        if len(word) == 5:
            f.write(word + '\n')
            words_count += 1
print(f'Найдено {words_count} слов из 5 букв')