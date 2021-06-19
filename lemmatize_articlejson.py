import json
import spacy
import pathlib
import os
import sys

banned = [  # lemmatization errors
    "\n\n\u3000", "\n\n", "\n", "日", "月", "年", "wます", "者", "県", "人",
    "的", "円", "市", "回", "中", "時", "店", "＝", "\u3000", "区", "約",
    "後", "b", "目", "数", "分", "性", "前", "内",
    # too generic
    "時間", "日本"
]

data_path = pathlib.WindowsPath(os.getcwd() + '/data')


def create_days_list():
    temp = data_path.iterdir()
    return [item.name for item in temp]


def lemmatize_day(day):
    nlp = spacy.load("ja_core_news_lg")
    day_folder_path = os.path.join(data_path, day)
    with open(day_folder_path + f"//{day}.json", encoding='utf-8') as file:
        articles = json.load(file)

    for art in articles:
        title = art['title']
        article = art['article']
        doc = nlp(title + "\n" + article)
        art_lemmas = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_digit and token.lemma_ not in banned:
                art_lemmas.append(token.lemma_)
        dct = dict([(i, art_lemmas.count(i)) for i in set(art_lemmas)])
        d_view = sorted(dct.items(), key=lambda x: x[1], reverse=True)
        art['article'] = d_view

    with open(day_folder_path + f"//{day}_lemmatized.json", mode='w', encoding='utf-8') as output:
        json.dump(articles, output, indent=4, sort_keys=True, ensure_ascii=False)
    print(f"lemmatized {day}")


def main(arg):

    if arg == 'all':
        days_list = create_days_list()
        for d in days_list:
            day = d
            lemmatize_day(day)
    else:
        day = arg
        lemmatize_day(day)


if __name__ == '__main__':
    main(sys.argv[1])
