import csv
import json

from matplotlib import pyplot as plt


with open('words_data.json', 'r', encoding='utf-8') as f:            # загрузка файла с баснями
    basni = json.load(f)

with open('most_heterogeneous.csv', 'r', encoding='utf-8') as f:        # загрузка файла с неоднородными словами
    reader = csv.DictReader(f, delimiter=',')
    words = []
    for row in reader:
        words.append(row["word"])


for word in words:
    y = []
    years = []      # список годов для подписей
    x = []
    count = 0
    for basnya in basni:
        for basnya_word in basnya['words']:
            count += 1
            x.append(count)
            years.append(basnya['date'])
            if basnya_word == word:
                y.append(1)                                             # формирование выборки индикаторов
            else:
                y.append(0)                                             # формирование выборки индикаторов
    fig = plt.figure(figsize=(25, 7))
    ax = fig.add_subplot()
    ax.plot(x, y)
    ax.set_ylim(0, 1)
    plt.xticks(x, years)
    plt.tick_params(axis='x', which='major', rotation=45)
    for tick in plt.gca().xaxis.get_major_ticks():
        tick.set_visible(False)
    for num in [0, 219, 1121, 2170, 3866, 6703, 11934, 12804, 14704, 17445, 19355, 22625,   # номера тех мест, где один год меняется на следующий
                22790, 22969, 25343, 25505, 29195, 29415, 30054, 32378, 33099, 33803]:
        plt.gca().xaxis.get_major_ticks()[num].set_visible(True)
    plt.xlabel("Год")
    plt.ylabel("Индикатор появления слова")
    plt.title(word)
    address = word + '.png'                                             # формирование адреса для сохранения графика
    plt.savefig(address)                                                # сохранение графика по указанному адресу
    plt.show()
