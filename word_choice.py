import re
import sys, os


# ---------------------- Фильтры --------------------------------
# Запретить слова в которых буква встречается больше 1 раза
ban = False # False

# Черный список букв
black_list = ''

# Буквы, которые есть в слове
# Первый элемент (ключ) это буква которая есть в слове
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



# Функция фильтрации слов
def filter_words(all_words, black_list, filter, ban):
    # Убираем слова, в которых есть буквы из черного списка
    black_list = set(black_list)
    words = []
    for word in all_words:
        word = word.rstrip()
        set_word = set(word)

        if set_word - black_list == set_word:
            words.append(word)


    # Подготовка фильтров
    letter_in_place = '.....'  # Буквы стоящие на своем месте
    letter_in_word = dict()  # Буквы есть в слове
    for letter, word in filter.items():
        if '+' in word:
            # Буквы стоящие на своем месте
            pos = word.index('+')
            letter_in_place = letter_in_place[:pos] + letter + letter_in_place[pos+1:]
        elif '-' in word:
            # Буквы есть в слове, но позиция неизвестна, известно только где буква не находится
            # Копируем в этот словарь элементы которые не относятся к Буквы стоящие на своем месте
            letter_in_word[letter] = word
    letter_in_place = re.compile(letter_in_place)  # Компилируем из строки объект регулярное выражение



    # Применяем фильтры и выводим прошедшие слова
    out_words = [] # Выведенные слова
    words_count = 0
    for word in words:
        check_ok = False
        if letter_in_place.fullmatch(word):
            if letter_in_word:
                # Если фильтр не задан, сюда попадут все слова
                for letter, sample in letter_in_word.items():
                    # Проходим по словарю с буквами, чье положение неизвестно
                    check = '' # Буквы которые надо проверить, если в них есть искомая, то слово проходит
                    for i, w in enumerate(word):
                        if sample[i] == '.':
                            # На этом месте может быть эта буква
                            check += w
                        else:
                            # На этом месте не может быть эта буква
                            if w == letter:
                                # но если она тут есть, бракуем слово сразу
                                check = ''
                                break
                    if letter in check:
                        # Буква есть в  месте где она может быть, слово принято
                        check_ok = True
                    else:
                        check_ok = False
                        break  # Если слово не прошло по одному из фильтров то оно не прошло вообще

            else:
                # Фильтров нет, пропускаем слово
                check_ok = True

        if check_ok:
            # Фильтр пропустил слово
            if ban and re.findall(r'(\w).*\1+', word):
                # В слове запрещены одинаковые буквы, а они есть
                pass
            else:
                print(word)
                words_count += 1
                out_words.append(word)

    print(f'\n {words_count} слова \n\n')
    return set(out_words)





# Чтение слов
input_file = os.path.join(sys.path[0], 'five_letters_words.txt')  # Файл ввода

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()
all_words = set(map(lambda x: x.rstrip(), all_words))  # Убираем дубликаты слов и перевод строки из них

# Алфавит отсортированный в порядке частотности букв в словах
alphabet = 'аиокреытлснупмбдвгзшячхфьжцйюэщъё'

# Слова будем выводить не всем списком, несколькими блоками, в порядке популярности букв встречающихся в них
# т.е. сначала будут идти слова которые состоят из самых часто встречаемых букв
# Блоки ограничиваются используемыми буквами, поэтому сначала будем запрещать все буквы и пытаться образовать слова
# далее будем добавлять по 1 букве (самой популярной из списка) и после каждого разрешения пытаться выводить слова
# буквы, которые находятся в черном списке, определенном пользователем, добавляться не будут, таким образом реализуя фильтр.
# после вывода каждого блока делаем пробел, а выведенные слова изымаем из общего списка, чтоб избежать повторения.

new_black_list = alphabet
for letter in alphabet:
    if letter in black_list:
        # Не включаем в слова буквы, которые запрещены пользователем
        continue
    new_black_list = new_black_list.replace(letter, '')
    all_words = all_words - filter_words(all_words, new_black_list, filter, ban) # Удаляем выведенные слова из общего списка

