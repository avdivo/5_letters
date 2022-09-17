# Создание групп слов с различными свойствами для Redis

import re
import sys, os
from redisworks import Root

root = Root()
root = Root(host='localhost', port=6379, db=0)
print(root['....ю'])
if root.all:
    exit()

# Чтение слов
input_file = os.path.join(sys.path[0], 'five_letters_singular.txt')  # Файл ввода

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()
all_words = set(map(lambda x: x.rstrip(), all_words))  # Убираем дубликаты слов и перевод строки из них
root.all = all_words # Запись в Redis полного словаря

# Подготовка русского алфавита
a = ord('а')
alphabet = ''.join([chr(i) for i in range(a,a+6)] + [chr(a+33)] + [chr(i) for i in range(a+6,a+32)])

# Создание групп с точно присутствующей буквой в слове на определенной позиции
# Создаем ключи для Redis указывающие на список слов в которых
# в одной из позиций стоит определенная буква. Пример ключа: а....
# Перебираются все буквы алфавита во всех 5 позициях в слове
group = set()
for pos in range(5):
    group_name = '.....'
    for letter in alphabet:
        group_name = group_name[:pos] + letter + '.' * (4 - pos)
        group.clear()
        for word in all_words:
            # Готовим можество слов, в которых заданная буква в нужной позиции
            if re.findall(group_name, word):
                group.add(word)
        if group:
            root[group_name] = group
            print(root[group_name])
exit()

# Для вывода в консоль и подсчета слов в группах
group = []
cou = 0
for pos in range(5):
    group_name = '.....'
    for letter in alphabet:
        group_name = group_name[:pos] + letter + '.' * (4 - pos)
        print('\n', group_name, '\n')
        group_len = 0
        for word in all_words:
            # Выводим слова, в которых заданная буква в нужной позиции
            if re.findall(group_name, word):
                cou += 1
                group_len += 1
                print(cou, word)
        group.append((group_name, group_len))

# Перечисление групп и их размеров
for i in group:
    print(*i)

exit()
#-------------------------------------------------------------
# Подготовка списка часто употребляемых букв
alphabet = 'аиокреытлснупмбдвгзшячхфьжцйюэщъё'

# Создание групп слов в которых нет определенной буквы
cou = 0
group = []
for letter in alphabet:
    group_name = 'no_' + letter
    # print('\n', group_name, '\n')
    group_len = 0
    for word in all_words:
        if letter not in word:
            cou += 1
            group_len += 1
            # print(cou, word)
    group.append((group_name, group_len))

# Перечисление групп и их размеров
for i in group:
    print(*i)

# Результат группировки не впечатлил. Размер групп не меньше половины,
# во многих случаяхблизок ко всему объему БД, при этом занимает много места в памяти.
# Использовать вероятно не буду.
