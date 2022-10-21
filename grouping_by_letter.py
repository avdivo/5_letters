# Группирова слов на наборам букв с сортировкой групп по количеству слов в ней
import sys, os

input_file = os.path.join(sys.path[0], 'five_letters_singular.txt')  # Файл со словами

with open(input_file, 'r', encoding='utf-8') as f:
    all_words = f.readlines()

kits = dict()
for word in all_words:
    word = word.strip()
    kit = ''.join(sorted(set(word)))
    try:
        kits[kit] += [word]
    except:
        kits[kit] = [word]

ma = 0
for k, v in kits.items():
    print(k, len(v))
    print(*v)
    print()
    if ma < len(v):
        ma = len(v)
print(len(kits), ma)