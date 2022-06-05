# Читаем файл со всеми русскими словами формируем список букв отсортированный по частоте использования в словах
import sys, os

input_file = os.path.join(sys.path[0], 'all_words.txt')  # Файл ввода

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()

letters = {
    'а': 0, 'б': 0, 'в': 0, 'г': 0, 'д': 0, 'е': 0, 'ё': 0, 'ж': 0, 'з': 0, 'и': 0, 'й': 0,
    'к': 0, 'л': 0, 'м': 0, 'н': 0, 'о': 0, 'п': 0, 'р': 0, 'с': 0, 'т': 0, 'у': 0, 'ф': 0,
    'х': 0, 'ц': 0, 'ч': 0, 'ш': 0, 'щ': 0, 'ъ': 0, 'ы': 0, 'ь': 0, 'э': 0, 'ю': 0, 'я': 0
}  # Буквы алфавита с частотой встречаемости

for word in all_words:
    for letter in word:
        if letter in letters:
            letters[letter] += 1

print(''.join([x for x in sorted(letters.keys(), key=lambda i: letters[i], reverse=True)]))

# Для всех слов:     иоаенрткслвпымдуязбгьчцшфжхщйюэъё

# Для слов из 5 букв:    аиокреытлснупмбдвгзшячхфьжцйюэщъё
