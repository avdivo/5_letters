import re
import redis
import time

# ---------------------- Фильтры --------------------------------
# Запретить слова в которых буква встречается больше 1 раза
ban = False  # False - разрешено
# Какая буква должна повторяться ('*' - любая)
double_letter = ''
# Черный список букв
black_list = ''
# Белый список букв (эти буквы объязательны в слове)
white_list = ''

# Буквы, которые есть в слове
# Если словарь или значение его элемента пустые, значит еще нет букв которые точно есть в слове.
# Если буквы есть, соварь будет содержать описание известных позиций в слове, позиции обозначаются ключами 0 - 4:
# Буква в верхнем регистре строки значения обозначает что в этой позиции точно стоит эта буква.
# В нижнем регистре буквы обозначают что в этой позиции этаи буквы не стоит (но она есть в слове в дргой позиции)
existing_letters = {0: 'А', 1: 'ш', 2: 'щр', 3: '', 4: ''}

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

# Отсев слов в которых нет букв из Белого списка
# Суммируем множества слов в которых нет объязательных букв и отнимаем его от слов, оставшихся после Черного списка
if white_list:
    # Запрашиваем у Redis сумму множеств
    list_group_name = [f'no_{letter}' for letter in white_list]
    all_words -= set(map(lambda x: x.decode('utf-8'), r.sunion(*list_group_name)))

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
#    местах кроме запрещенного. Отнимаем от него множество с этой буквой в запрещенной позиции,
#    чтобы избежать попадания такого слова, когда нужных букв в слове не одна.
#    Запоминаем это множкство в python для первй буквы.
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
                        # Для букв которые стоят
                        exist_out_of_position &= set(map(lambda x: x.decode('utf-8'),
                                                         r.sunion(exist_out_of_position_inverse)))
                    else:
                        exist_out_of_position = set(map(lambda x: x.decode('utf-8'),
                                                        r.sunion(exist_out_of_position_inverse)))
                        # print(exist_out_of_position_inverse, len(exist_out_of_position))
                    # При 2 искомых буквах в слове. Слово будет включно в список, поскольку имеет
                    # нужную букву там где она не запрещена, однако оно же может иметь букву в позиции
                    # где она запрещена. Поэтому очистим список от слов имеющих букву в запрещенной позиции
                    exist_out_of_position -= set(map(lambda x: x.decode('utf-8'),
                                                        r.sunion('.....'[:pos] + letter + '.' * (4 - pos))))
                    exist_out_of_position_inverse.clear()
            else:
                # Для букв которые стоят на своих позициях
                exist_in_position.add('.....'[:pos] + val[0].lower() + '.' * (4 - pos))
    if exist_in_position:
        exist_in_position = set(map(lambda x: x.decode('utf-8'), r.sinter(exist_in_position)))
        all_words &= exist_in_position
    if exist_out_of_position:
        all_words &= exist_out_of_position

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
    # Исключаем слово, если заданные буквы не встречаются в нем более 1 раза
    if double_letter:
        if double_letter != '*':
            stop = False
            for letter in double_letter:
                if word.count(letter) < 2:
                    stop = True
                    break
            if stop:
                continue
        else:
            # Исключаем слово, если в нем нет дубля любой буквы
            if not re.findall(r'(\w).*\1+', word):
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
