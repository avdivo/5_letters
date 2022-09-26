import re
import redis
import time

# ---------------------- Фильтры --------------------------------
# Запретить слова в которых буква встречается больше 1 раза
ban = False  # False - разрешено

# Черный список букв
black_list = 'ко'

# Буквы, которые есть в слове
# Если словарь или значение его элемента пустые, значит еще нет букв которые точно есть в слове.
# Если буквы есть, соварь будет содержать описание известных позиций в слове, позиции обозначаются ключами 0 - 4:
# Буква в верхнем регистре строки значения обозначает что в этой позиции точно стоит эта буква.
# В нижнем регистре буквы обозначают что в этой позиции этаи буквы не стоит (но она есть в слове в дргой позиции)
existing_letters = {0: '', 1: 'а', 2: '', 3: '', 4: ''}  # dict()

# ---------------------------------------------------------------
# ------------------- Время выполнения ----------------------
start_time = time.time()
# ------------------- Время выполнения ----------------------

# Подготовка алфавита
alphabet = 'аокеритлнсупмбвдзгяышьцчхйфжюэщъё-'

r = redis.Redis(host='localhost', port=6379, db=0)  # Подключаемся к Redis

# Проверяем существование базы данных слов по ключу 'all'
if not r.exists("all"):
    exit()  # Создаем базу данных


# ------------------------ Фильтр слов ---------------------------------
# Отсев слов которые содержат буквы из Черного списка
# Запрашиваем в Redis слова, в которых нет букв из черного списка
# Слова записаны в группы 'no_x' где x отсутствующая буква
if black_list:
    # Запрашиваем у Redis пересечение множеств.
    list_group_name = [f'no_{letter}' for letter in black_list]
    all_words = set(map(lambda x: x.decode('utf-8'), r.sinter(*list_group_name)))
else:
    # Если Черный список пуст, читаем множество со всеми словами
    all_words = set(map(lambda x: x.decode('utf-8'), r.smembers('all')))

# Подготовка фильтров на основе присутствующих в слове букв
# Готовим список ключей множеств Redis
# Работа фильтров:
# Имеются группы слов в каждой из которых одна из букв алфавита стоит в одой из пяти позици в слове
# Для каждой буквы алфавита и каждой позиции. Они имеют имена по шаблону: а.... или ..о..
# 1. Для нахождения слов с известными буквами в известных позициях (приходят как заглавные)
#    включаем соответствующую группу в список, и находим пересечение (средствами Redis)
#    всех списков. Запоминаем полученное множество в Python.
# 2. Для случаев когда известно, что буква есть в слове и позиция
#    где эта буква не стоит. Получаем множества (суммируем) где бука есть на всех дпугих
#    местах кроме запрещенного запоминаем это множкство в python для первй буквы.
#    Для остальных букв находим пересечение с запомненным множеством и сохраняем туда же.
# 3. Находим пересечение множеств после п.1 и п.2
if existing_letters:
    exist_in_position = set()
    exist_out_of_position = set()
    exist_out_of_position_inverse = set()
    for pos, val in existing_letters.items():
        if val:
            if val.islower():
                for letter in val:
                    # Добавляем имена групп с данной буквой, кроме того, где она стоит в рассматриваемой
                    # позиции, слова где эта буква в этой позиции не включаются
                    for i in range(5):
                        if i != pos:
                            # Ключи множеств, где буква находится в не запрещенных местах
                            exist_out_of_position_inverse.add(f'....{letter}....'[4-i:9-i])
                        # else:
                        #     # Ключ множества, где буква находится в запрещенном месте
                        #     exist_out_of_position.add('.....'[:pos] + letter + '.' * (4 - pos))
                    if exist_out_of_position:
                        exist_out_of_position &= set(map(lambda x: x.decode('utf-8'),
                                                        r.sunion(exist_out_of_position_inverse)))
                    else:
                        exist_out_of_position = set(map(lambda x: x.decode('utf-8'),
                                                        r.sunion(exist_out_of_position_inverse)))
                    exist_out_of_position_inverse.clear()
            else:
                # Для букв которые стоят на своих позициях
                exist_in_position.add('.....'[:pos] + val[0].lower() + '.' * (4 - pos))
    if exist_in_position:
        exist_in_position = set(map(lambda x: x.decode('utf-8'), r.sinter(exist_in_position)))
        all_words &= exist_in_position
    if exist_out_of_position:
        all_words &= exist_out_of_position

# print(all_words)
# print(len(all_words))
# print(exist_out_of_position)
# print(len(exist_out_of_position))
# # ------------------- Время выполнения ----------------------
# print(f"{(time.time() - start_time) * 1000} миллисекунд")
# # ------------------- Время выполнения ----------------------
#
# exit()


# out_words = sorted(list(all_words))
# out_words_len = len(all_words)
# columns = 20
# if out_words:
#     for i in range(out_words_len // columns + int(out_words_len % columns > 0)):
#         print(*out_words[i * columns:i * columns + columns])
# print(f'\n{out_words_len} слов всего')
# exit()



# Разбивка на группы и сортировка перед выводом
# Слова для вывода разбиваем по группам.
# Группы формируются по принципу частотности использования групп в 5-буквенных словах
# Для этого определяем для каждого слова, какая его буква стоит ниже всех в списке частотности букв
# По индексу этой буквы назначаем номер группы для вывода
number_group = dict()
summ = 0
for word in all_words:
    # Исключаем слова, с дублированием букв
    if ban and re.findall(r'(\w).*\1+', word):
        continue
    number = max([alphabet.index(letter) for letter in word])
    try:
        number_group[number] += [word]
    except:
        number_group[number] = [word]
    summ += 1
number_group = sorted(number_group.items(), key=lambda x: x[0])

for i, l in enumerate(number_group):
    if l:
        out_words = sorted(l[1])
        out_words_len = len(out_words)
        # Выводим слов на экран столбцами
        print(f'\nГруппа {i+1} ({out_words_len} слов):')
        columns = 20
        if out_words:
            for i in range(out_words_len // columns + int(out_words_len % columns > 0)):
                print(*out_words[i * columns:i * columns + columns])
print(f'\n{summ} слов всего')

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