import sys
from selenium import webdriver
import time
import json
import pathlib
import os
import lemmatize_articlejson

startpage = 1
data_path = pathlib.WindowsPath(os.getcwd() + '/data')

def get_articles(page_num, month, day):

    def click_see_full_article():
        try:
            driver.find_element_by_xpath("//article/div[2]/div/p/a").click()
        except:
            driver.refresh()
            time.sleep(3)

    def get_article_text():
        retries = 0
        try:
            return "\n\n".join([i.text for i in driver.find_elements_by_xpath("//article/div[1]/div/p")])
        except:
            if retries < 3:
                retries += 1
                driver.refresh()
                time.sleep(3)
                get_article_text()
            return ""

    def get_comments_number():
        try:
            return int(driver.find_element_by_class_name("count").text)
        except:
            return 0

    try:

        #arguments are month and day of the articles you want as int
        driver.get(f"https://news.yahoo.co.jp/topics/top-picks?page={page_num}")
        for index in range(25):
            title = driver.find_elements_by_class_name('newsFeed_item_title')[index]
            item_date = driver.find_elements_by_class_name('newsFeed_item_date')[index].text
            # checks if the article's date is today or the tomorrow (time zone problems), stops on the day before
            title_text = title.text
            art_month, art_day = list(map(int, item_date.split("(")[0].split("/")))
            #if we found the day then get the article's data
            if art_day == day_tosearch and art_month == month_tosearch:
                title.click()
                time.sleep(3)
                click_see_full_article()
                time.sleep(3)
                article = get_article_text()
                url = driver.current_url
                comments_number = get_comments_number()
                result.append({'article': article, 'title': title_text, 'url': url, 'comments_num': comments_number})
                print(f"\tGot article {title_text} at \n{url}")
                driver.get(f"https://news.yahoo.co.jp/topics/top-picks?page={page_num}")
            if art_day > day and art_month == month:
                continue
            if art_month < month or art_day < day:
                return result

        return get_articles(page_num + 1, month, day)

    except:
        print("PAGES ENDED, VERY BAD")
        return


if __name__ == '__main__':
    try:

        date_to_search = sys.argv[1]
        day_folder_path = os.path.join(data_path, date_to_search)
        month_tosearch, day_tosearch = list(map(int, date_to_search.split("_")))

        driver = webdriver.Firefox()
        result = []

        articles = get_articles(startpage, month_tosearch, day_tosearch)

        os.mkdir(day_folder_path)

        with open(day_folder_path + f"//{date_to_search}.json", mode='w', encoding='utf-8') as output:
            json.dump(articles, output, indent=4, sort_keys=True, ensure_ascii=False)

        lemmatize_articlejson.main(date_to_search)

    except:
        print("argument needs to be like: 6_04 (june 4th)")

