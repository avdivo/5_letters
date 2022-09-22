import re
import redis
import time

# ---------------------- Фильтры --------------------------------
# Запретить слова в которых буква встречается больше 1 раза
ban = False  # False

# Черный список букв
black_list = ''

# Буквы, которые есть в слове
# Первый элемент (ключ) - это буква, которая есть в слове
# Вместо точки ставим + если буква находится в этой позиции
# Вместо точки ставим - если буква не находится в этой позиции
filter = {
    '': '.....',
    '': '.....',
    '': '.....',
    '': '.....',
    '': '.....'
}


# ---------------------------------------------------------------
# ------------------- Время выполнения ----------------------
start_time = time.time()
# ------------------- Время выполнения ----------------------

r = redis.Redis(host='localhost', port=6379, db=0)

# Запрашиваем в Redis слова, в которых нет букв из черного списка
# Слова записаны в группы 'no_x' где x отсутствующая буква
if black_list:
    list_group_name = [f'no_{letter}' for letter in black_list]
    all_words = set(map(lambda x: x.decode('utf-8'), r.sinter(*list_group_name)))
else:
    all_words = set(map(lambda x: x.decode('utf-8'), r.smembers('all')))

# Слова для вывода разбиваем по группам.
# Группы формируются по принципу частотности использования групп в 5-буквенных словах
# Для этого определяем для каждого слова, какая его буква стоит ниже всех в списке частотности букв
# По индексу этой буквы назначаем номер группы для вывода

# Алфавит отсортированный в порядке частотности букв в словах
alphabet = 'аокеритлнсупмбвдзгяышьцчхйфжюэщъё-'

number_group = dict()
for word in all_words:
    number = max([alphabet.index(letter) for letter in word])
    try:
        number_group[number] += [word]
    except:
        number_group[number] = [word]
for i, group in number_group.items():
    print(f'Группа {i} - {len(group)} слов:\n{sorted(group)}\n')



# ------------------- Время выполнения ----------------------
print(f"{(time.time() - start_time)*1000} миллисекунд")
# ------------------- Время выполнения ----------------------
exit()


def filter_words(all_words: set, black_list: str, filter: dict, ban: bool):
    ''' Фильтр слов. Принимает:
    Словарь (set), список букв которые должны отсутствовать в выбранных словах (str),
    фильтр (dict) - key - буква, value - 5 символов ( '.' - любая буква, '+' - в этой
    позиции буква key, '-' - в этой позиции нет буквы key),
    разрешать ли слова с повторяющейся буквой'''

    # Подготовка фильтров
    # список писков по количеству букв в слове, каждый соответствует позиции буквы
    # в списках перечислены буквы которые не могут находиться на этой позиции в слове
    position_not_for_letter = [[] for _ in range(5)]
    pattern = ['.' for _ in range(5)]  # На каждой позиции буква которая должна на ней быть
    white_list_letter = []  # Объязательные буквы в слове
    for letter, positions in filter.items():
        if letter:
            white_list_letter.append(letter)
            for i in range(5):
                if positions[i] == '+':
                    pattern[i] = letter
                elif positions[i] == '-':
                    position_not_for_letter[i].append(letter)
    pattern = re.compile(''.join(pattern))
    black_list = set(black_list)
    out_words = []

    # Запрашиваем в Redis слова, в которых нет букв из черного списка
    # Слова записаны в группы 'no_x' где x отсутствующая буква
    if black_list:
        list_group_name = [f'no_{letter}' for letter in black_list]
        all_words = set(map(lambda x: x.decode('utf-8'), r.sinter(*list_group_name)))

    # Исключаем слова, в которых нет нужных букв в нужных позициях
    # if not re.findall(pattern, word):
    #     continue

    # Исключаем слова, в которых нет объязательных буквы
    # block = False
    # for letter in white_list_letter:
    #     if letter not in word:
    #         block = True
    # if block:
    #     continue

    # Исключаем слова, в которых есть буквы, стоящие не на своих позициях
    # block = False
    # for i, letter in enumerate(word):
    #     if letter in position_not_for_letter[i]:
    #         block = True
    # if block:
    #     continue

    # Исключаем слова, с дублированием букв
    # if ban and re.findall(r'(\w).*\1+', word):
    #     continue

    # out_words.append(word)  # Слово прошло все фильтры и будет выведено

    return all_words

# ------------------- Время выполнения ----------------------
start_time = time.time()
# ------------------- Время выполнения ----------------------


# ------------------------- Удаляем -------------------------
# Чтение слов
# input_file = os.path.join(sys.path[0], 'five_letters_singular.txt')  # Файл ввода
#
# with open(input_file, 'r', encoding='utf-8') as f:
#     all_words = f.readlines()
# all_words = set(map(lambda x: x.rstrip(), all_words))  # Убираем дубликаты слов и перевод строки из них
# ------------------------- Удаляем -------------------------

r = redis.Redis(host='localhost', port=6379, db=0)
all_words = set(map(lambda x: x.decode('utf-8'), r.smembers('all')))

# new = r.sunion('а.....', '.а...', '..а..', '...а.', '....а')
# print(len(new))
# print(new)


print(f"{(time.time() - start_time)*1000} миллисекунд")
# exit()
# Алфавит отсортированный в порядке частотности букв в словах
alphabet = 'аокеритлнсупмбвдзгяышьцчхйфжюэщъё'

# Слова будем выводить не всем списком, несколькими блоками, в порядке популярности букв встречающихся в них
# т.е. сначала будут идти слова которые состоят из самых часто встречаемых букв
# Блоки ограничиваются используемыми буквами, поэтому сначала будем запрещать все буквы и пытаться образовать слова
# далее будем добавлять по 1 букве (самой популярной из списка) и после каждого разрешения пытаться выводить слова
# буквы, которые находятся в черном списке, определенном пользователем, добавляться не будут, таким образом реализуя фильтр.
# после вывода каждого блока делаем пробел, а выведенные слова изымаем из общего списка, чтоб избежать повторения.

print()
summ = 0  # Всего слов
new_black_list = alphabet
for letter in alphabet:
    if letter in black_list:
        # Не включаем в слова буквы, которые запрещены пользователем
        continue
    new_black_list = new_black_list.replace(letter, '')

    out_words = filter_words(all_words, new_black_list, filter, ban)  # Фильтруем слова
    out_words_len = len(out_words)
    summ += out_words_len  # Всего слов выводится
    all_words = all_words - out_words  # Удаляем из словаря выведенные слова
    out_words = sorted(list(out_words))


    # Выводим слов на экран столбцами
    columns = 20
    if out_words:
        for i in range(out_words_len // columns + int(out_words_len % columns > 0)):
            print(*out_words[i * columns:i * columns + columns])
        print(f'\n{out_words_len} слов\n')

print(f'{summ} слов всего')

# ------------------- Время выполнения ----------------------
print(f"{(time.time() - start_time)*1000} миллисекунд")
# ~ 200 - 250, бывает 150
# ------------------- Время выполнения ----------------------