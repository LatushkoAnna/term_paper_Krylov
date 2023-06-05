import json
import pymorphy2
import numpy as np
import collections
import math
import csv
from scipy.special import kolmogorov
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt


textfile = open("basni.txt", 'r', encoding='UTF-8')         # загрузка файла с текстами басен

ListOfLines = []
ListOfNames = []
ListOfTexts = []
ListOfDates = []
AllTheText = []


lines = textfile.readlines()

for line in lines:
    line.replace('\n', ' ')

for i in range(len(lines) - 1):
    if i == 0 and lines[i] != '\n' and lines[i + 1] == '\n':
        line = lines[i]
        line = line.replace('\n', '')                       # удаление пустых строк
        ListOfNames.append(line)                            # сохранение названий
    if i > 0 and lines[i] != '\n' and lines[i + 1] == '\n' and lines[i - 1] == '\n':
        line = lines[i]
        line = line.replace('\n', '')                       # удаление пустых строк
        ListOfNames.append(line)                            # сохранение названий

morph = pymorphy2.MorphAnalyzer()

for i in range(len(lines) - 1):
    if (i == 0 or (i > 0 and lines[i - 1] == '\n')) and lines[i] != '\n' and lines[i + 1] != '\n':
        j = i
        ListText = []
        while lines[j] != '\n' and len(lines[j]) != 0:
            line = lines[j]
            line = line.replace('\n', '')
            for sym in '.,:;«»“”!?—"_()<>':
                line = line.replace(sym, '')
            line = line.replace(" -", "")
            line = line.replace(" - ", " ")                 # удаление знаков препинания
            line = line.lower()
            if lines[j + 1] != '\n':
                for word in line.split():
                    ListText.append(morph.parse(word)[0].normal_form)
            else:
                if line.startswith('17') or line.startswith('18'):
                    ListOfDates.append(int(line))           # добавление известной даты
                    AllTheText.extend(ListText)             # добавление текста
                else:
                    for word in line.split():
                        ListText.append(morph.parse(word)[0].normal_form)       # добавление нормализованного слова
                    ListOfDates.append('Unknown')           # добавление неизвестной даты
            j = j + 1
        ListOfTexts.append(ListText)

data = []
for i in range(len(ListOfNames)):
    if ListOfDates[i] != 'Unknown':
        basnya = {'title': ListOfNames[i], 'date': ListOfDates[i], 'collected_works': 0, 'words': ListOfTexts[i]}
        data.append(basnya)             # создание словаря басен

basni = sorted(data, key=lambda d: d['date'])               # сортировка басен по году написания

with open('words_data.json', 'w', encoding='UTF-8') as f:        # сохранение словаря басен в JSON файл
    json.dump(basni, f, ensure_ascii=False, indent=4)

sorted_all_words = []
for basnya in basni:
    sorted_all_words.extend(basnya['words'])

words_count = collections.Counter(sorted_all_words)
for word in sorted_all_words:
    if words_count[word] < 2:
        del words_count[word]                               # удаление из списка слов, которые встречаются менее 2 раз
at_least_two = list(words_count)

emp_bridge = {}
summ_occurrences = {}
total_occurrences = {}
counter = 0
for word in at_least_two:
    dates = []
    summ_occurrences[word] = words_count[word]
    sample = []
    word_occurrences = []
    for basnya in basni:
        sample.extend([int(i) for i in [basnya_word == word for basnya_word in basnya['words']]])
        dates.extend([basnya['date'] for basnya_word in basnya['words']])
        basnya_words_count = collections.Counter(basnya['words'])
        if basnya_words_count[word]:
            word_occurrences.append(basnya_words_count[word])           # формирование выборки для расчёта эмпирического моста
        else:
            word_occurrences.append(0)                                  # формирование выборки для расчёта эмпирического моста
    total_occurrences[word] = word_occurrences

    # расчёт эмпирического моста
    y = np.array(sample)
    ymean = np.mean(y)
    y2 = []
    for i in range(len(y)):
        y2.append(y[i] ** 2)
    y2mean = np.mean(np.array(y2))
    sy2 = y2mean - ymean ** 2
    nsy2 = math.sqrt(len(y) * sy2)
    sums = []
    sum = 0
    for i in range(len(y)):
        sums.append(sum)
        sum += y[i]
    sums.append(sum)
    q = []
    for i in range(len(sums)):
        qi = (sums[i] - (i * sums[-1]) / len(y)) / nsy2
        q.append(abs(qi))
    if np.isnan(max(q)):
        pass
    else:
        emp_bridge[word] = [max(q), dates[q.index(max(q))]]
    counter += 1
    print(f'{counter}. {word}')
sorted_tuples = sorted(emp_bridge.items(), key=lambda item: item[1])           # сортировка максимумов эмпирического моста
sorted_emp = {k: v for k, v in sorted_tuples}
sample = []
for word in sorted_emp:
    sample.append(sorted_emp[word][0])

# сохранение максимумов эмпирического моста в JSON файл
with open('words_emp_bridge.csv', 'w', encoding='UTF-8', newline='') as f:
    fieldnames = ["word", "max_emp_bridge", "date_of_max", "occurrences"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for word in emp_bridge:
        temp_dict = {'word': word, 'max_emp_bridge': emp_bridge[word][0], "date_of_max": emp_bridge[word][1], 'occurrences': words_count[word]}
        writer.writerow(temp_dict)

# построение графиков ECDF и Kolmogorov CDF для максимумов эмпирического моста
x = np.array(sample)
y = []
temp = kolmogorov(x)
for i in temp:
    y.append(1-i)
res = ECDF(x)
plt.xlabel('Max emp bridge')
plt.ylabel('CDF')
plt.plot(x, y, 'b', label='Kolmogorov CDF')
plt.plot(res.x, res.y, 'r', label='ECDF')
plt.legend(fontsize=10)
plt.savefig('ecdf_kolmogorov_cdf.png')          # сохранение файла с графиком по указанному адресу
plt.show()
