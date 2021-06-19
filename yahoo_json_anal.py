import json
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import os
import sys
import statistics
import functools
import scipy
from scipy.stats import norm, kurtosis

data_path = pathlib.WindowsPath(os.getcwd() + '/data')

banned = [  # lemmatization errors
    "\n\n\u3000", "\n\n", "\n", "日", "月", "年", "ます", "者", "県", "人",
    "的", "円", "市", "回", "中", "時", "店", "＝", "\u3000", "区", "約",
    "後", "b", "目", "数", "分", "性", "前", "内", "氏", "会", "国", "第",
    "化", "所", "局", "\n\u3000", "\u3000\u3000", "点", "校", "省", "社",
    "法", "mm", "流", "大", "開く", "代", "g", "って", "～", "だ", "", "", "", "", "",
    # too generic
    "時間", "日本", "朝", "町", "言う", "思う", "受ける", "見る"
]

corona = [  # corona related words
    "コロナ", "ワクチン", "ウイルス", "感染", "接種", "延長", "宣言", "政府", "緊急"
]

olympics = [
    "五輪", "選手"
]


def plot_hysto(title, list_to_plot):
    plt.figure(figsize=(10, 5))  # size
    plt.rcParams["font.family"] = "MS Gothic"  # to make fonts readable
    plt.xticks(rotation=40)  # tilts xticks labels
    plt.title(title)

    y = np.array([i[1] for i in list_to_plot])
    x = np.array([i[0] for i in list_to_plot])

    plt.bar(x, y, width=0.5, color=['green'])


def day_total(day, plot=0, want_exclusions=0, first_n_elements=20):
    result = {}
    corona_related = {key: 0 for key in corona}
    olympics_related = {key: 0 for key in olympics}
    day_folder_path = os.path.join(data_path, day)
    with open(day_folder_path + f"//{day}_lemmatized.json", encoding='utf-8') as file:
        articles = json.load(file)
    for art in articles:
        for lemma in art['article']:
            if lemma[0] in banned:
                break
            if lemma[0] in corona:
                corona_related[lemma[0]] += lemma[1]
            if lemma[0] in olympics:
                olympics_related[lemma[0]] += lemma[1]
            if lemma[0] in result and lemma[0] not in corona and lemma[0] not in olympics:
                result[lemma[0]] += lemma[1]
            else:
                result[lemma[0]] = lemma[1]
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    if want_exclusions == 1:
        if plot:
            plot_hysto(day, result[:first_n_elements])
            plt.show(block=True)
        else:
            return result, corona_related, olympics_related
    else:
        if plot:
            plot_hysto(day, result[:first_n_elements])
            plt.show(block=True)
        else:
            return result


def word_through_days(word, plot=1):
    def create_days_list():
        temp = data_path.iterdir()
        return [item.name for item in temp]

    days_to_check = create_days_list()

    result = []
    for day in days_to_check:
        day_lemmas = day_total(day)
        found = tuple(filter(lambda x: x[0] == word, day_lemmas))
        if len(found) == 0:
            found = (day, 0)
            result.append(0)
            continue
        result.append(found[0][1])

    if plot:
        plot_hysto(word, list(zip(days_to_check, result)))
        plt.show(block=True)
    else:
        return list(zip(days_to_check, result))


def words_anal():
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
    if args[0] == '-word_through_days':
        word_through_days(*args[1:])
    if args[0] == '-words_anal':
        words_anal()

