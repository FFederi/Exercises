import json
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import os
import sys
import statistics
import functools
import scipy
import spacy
from scipy.stats import norm, kurtosis

nlp = spacy.load("ja_core_news_lg")
stpwds = spacy.lang.ja.stop_words.STOP_WORDS

data_path = pathlib.WindowsPath(os.getcwd() + '/data')

banned = [  # lemmatization errors
    "\n\n\u3000", "\n\n", "\n", "日", "月", "年", "ます", "者", "県", "人",
    "的", "円", "市", "回", "中", "時", "店", "＝", "\u3000", "区", "約",
    "後", "b", "目", "数", "分", "性", "前", "内", "氏", "会", "第",
    "化", "所", "局", "\n\u3000", "\u3000\u3000", "点", "校", "省", "社",
    "法", "mm", "流", "大", "代", "g", "って", "～", "だ", "", "", "", "", ""
]

corona = [  # corona related words
    "コロナ", "ワクチン", "ウイルス", "感染", "接種", "延長", "宣言", "政府", "緊急", "事態"
]

olympics = [
    "五輪", "選手", "観客", "オリンピック", "開催"
]


def plot_hysto(title, list_to_plot, vertical=0):
    plt.rcParams['xtick.major.pad'] = '4'
    plt.rcParams["font.family"] = "MS Gothic"  # to make fonts readable
    plt.figure(figsize=(10, 5))  # size
    plt.xticks(rotation=0)  # tilts xticks labels
    plt.title(title)

    if vertical:
        for item in list_to_plot:
            item[0] = '\n'.join(item[0][i:i + 1] for i in range(0, len(item[0]), 1))
    y = np.array([i[1] for i in list_to_plot])
    x = np.array([i[0] for i in list_to_plot])

    plt.bar(x, y, width=0.5, color=['green'])


def day_total(day, plot=0, block_stopwords=0, first_n_elements=20):
    block_stopwords = int(block_stopwords)
    result = {}
    day_folder_path = os.path.join(data_path, day)
    with open(day_folder_path + f"//{day}_lemmatized.json", encoding='utf-8') as file:
        articles = json.load(file)
    for art in articles:
        for lemma in art['article']:
            if lemma[0] in banned:
                continue
            if lemma[0] in stpwds and block_stopwords:
                continue
            if lemma[0] in result.keys():
                result[lemma[0]] += lemma[1]
            else:
                result[lemma[0]] = lemma[1]

    result = sorted(result.items(), key=lambda x: x[1], reverse=True)

    if plot:
        plot_hysto(day, result[:first_n_elements], 1)
        plt.show(block=True)
    else:
        return result


def words_through_days(arg, plot=1):
    def create_days_list():
        temp = data_path.iterdir()
        return [item.name for item in temp]

    days_to_check = create_days_list()

    if type(arg) == str:
        word = arg
        filter_fun = lambda x: x[0] == word
    elif type(arg) == list:
        wanted_lst = arg
        filter_fun = lambda x: x[0] in wanted_lst

    result = []
    for day in days_to_check:
        day_lemmas = day_total(day)
        found = tuple(filter(filter_fun, day_lemmas))
        if len(found) == 0:
            found = (day, 0)
            result.append(0)
            continue
        result.append(found[0][1])

    if plot:
        plot_hysto(arg, list(zip(days_to_check, result)), 1)
        plt.show(block=True)
    else:
        return list(zip(days_to_check, result))


def words_anal(block_stopwords=1, plot=0):
    block_stopwords = int(block_stopwords)
    def create_days_list():
        temp = data_path.iterdir()
        return [item.name for item in temp]

    days_to_check = create_days_list()

    def words_frequency():
        def create_key_or_update(key, value):
            if key in wrd_freq.keys():
                wrd_freq[key].append(value)
            if key not in wrd_freq.keys():
                wrd_freq[key] = [value]

        wrd_freq = {}
        if block_stopwords:
            lemmas_through_days = [dict(day_total(date, 0, 1)) for date in days_to_check]
        else:
            lemmas_through_days = [dict(day_total(date)) for date in days_to_check]
        total_words = list(set([item for sublist in lemmas_through_days for item in sublist]))
        for w in total_words:
            for day_dct in lemmas_through_days:
                if w in day_dct:
                    create_key_or_update(w, day_dct[w])
                if w not in day_dct:
                    create_key_or_update(w, 0)

        return wrd_freq


    result = []
    words = words_frequency()
    if plot:
        for key, value in words.items():
            value = sum(value)
            result.append([key, value])

        result = sorted(result, key=lambda x: x[1], reverse=True)
        plot_hysto('ciao', result[:30], 1)
        plt.show(block=True)
        return

    for word, occurs in words.items():
        dev = statistics.stdev(occurs)
        kurt = scipy.stats.kurtosis(occurs)
        if functools.reduce(lambda x, y: x + y, occurs) > 30:
            result.append([word, occurs, dev, kurt])

    kurt_sort = sorted(result, key=lambda x: x[3], reverse=True)
    with open("dev_sort_kurt.txt", "w", encoding='utf-8') as file:
        for lst in kurt_sort:
            file.write(f"{lst}\n")

    dev_sort = sorted(result, key=lambda x: x[2], reverse=True)
    with open("dev_sort_dev.txt", "w", encoding='utf-8') as file:
        for lst in dev_sort:
            file.write(f"{lst}\n")

    for item in result:
        item[1] = sum(item[1])
    freq_sort = sorted(result, key=lambda x: x[1], reverse=True)
    with open("dev_sort_freq.txt", "w", encoding='utf-8') as file:
        for lst in freq_sort:
            file.write(f"{lst}\n")

# plt.savefig(day_folder_path + f"//{day}.png")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: first arg is function to call")
        exit()
    if args[0] == '-day_total':
        day_total(*args[1:])
    if args[0] == '-words_through_days':
        if args[1] == 'corona':
            words_through_days(corona)
        elif args[1] == 'olympics':
            words_through_days(olympics)
        elif args[1]:
            words_through_days(*args[1:])
    if args[0] == '-words_anal':
        words_anal(*args[1:])

