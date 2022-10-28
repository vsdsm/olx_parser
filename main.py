import csv
import pandas as pd
import requests
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os
import random
import time
import datetime

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"

}
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
options.add_argument("--headless")
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(
    executable_path=r'C:\Users\Vadym\Documents\projects\olx_parser\chromedriver\chromedriver.exe',
    options=options
)
driver.maximize_window()

#шукаю по запиту та скачую результати пошуку
def get_source_html(url, search_text):
    # driver = webdriver.Chrome(
    #     executable_path=r'C:\Users\Vadym\Documents\projects\olx_parser\chromedriver\chromedriver.exe',
    #     options=options
    # )
    # driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)
        search_input = driver.find_element(By.ID, "headerSearch").send_keys(f"{search_text}")
        time.sleep(3)
        search_btn = driver.find_element(By.ID, "submit-searchmain").click()
        time.sleep(4)
        count = 1

        with open(f'pages_search_result/{search_text}_{count}.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        print(f"Processing page {count}")

        count += 1

        while True:

            driver.get(url+"/d/uk/list/q-"+f"{search_text.replace(' ', '-')}"+f'/?page={count}')
            curr_page = int(driver.current_url.split("=")[1])
            print(curr_page)
            time.sleep(3)
            if curr_page < count:
                print("End of pages")
                break
            with open(f'pages_search_result/{search_text}_{count}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
            print(f"Processing page {count}")

            count += 1
            time.sleep(3)

    except Exception as ex:
        print(ex)
    finally:
        # driver.close()
        # driver.quit()
        print("THE END")

#збираю url результатів пошуку та зберігаю їх у файл urls.txt
def get_item_url(file_path): #збір урл кожного

    with open(file_path, "r", encoding="utf-8") as file:
        src = file.read()
    file = open(r"C:\Users\Vadym\Documents\projects\olx_parser\urls.txt", "w")
    file.close()
    soup = BeautifulSoup(src, "lxml")
    item_divs = soup.find_all("a", class_="css-1bbgabe")

    urls = []

    for item in item_divs:
        try:
            item_url = item.get("href")
            urls.append("https://www.olx.ua"+item_url)

        except Exception as ex:
            print(ex)
            continue
    for i in urls:
        with open(r"C:\Users\Vadym\Documents\projects\olx_parser\urls.txt", "a") as file:
            file.write(f"{i}\n")
    print(len(urls), urls)
def paste_urls_into_txt(): #пройтись по кожному хтмл й взяти лінк
    os.chdir("pages_search_result")
    pages_list = os.listdir()
    print(pages_list)
        #створюю новий .csv файл та роблю в ньому потрібні колонки
    with open("result.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "item_name",
                "url",
                "item_city",
                "item_price",
                "item_pablication_date",
                "item_status",
                "item_description",
                "item_id",
                "item_negotiations",
                "item_views",
                "item_biz_or_fiz",
                "item_saller_name",
                "item_saller_work_time"
             )
        )
    for i in pages_list:
        if ".html" in i:
            get_item_url(i)
            clear_links(i)
            get_data(f"C:/Users/Vadym/Documents/projects/olx_parser/{i}_urls_clear.txt")
    driver.close()
    driver.quit()
    print("Програма зібрала дані та завершила роботу!")

#почистити список посилань та зберегти лише унікальні в файлі urls_clear.txt
def clear_links(count):
    with open(r"C:\Users\Vadym\Documents\projects\olx_parser\urls.txt", "r") as file:
        all_links = file.read()

    all_links_list = all_links.split("\n")[:-1]
    clear_list_links = set(all_links_list)
    print(clear_list_links)

    for i in clear_list_links:
        with open(f"C:/Users/Vadym/Documents/projects/olx_parser/{count}_urls_clear.txt", "a") as file:
            file.write(f"{i}\n")

#проходжуся по кожній сторінці з посилань, зберігаю її, витягую потрібні дані, зберігаю ці дані в .csv, .xlsx, .json
def get_data(file_path):
    #результуючий список для збору усіх даних
    result_list = []

    #витягую url адреси з файла
    with open(file_path) as file:
        url_list = file.readlines()
        url_list = [url.strip() for url in url_list]

    result_list = []
    count = 1
    urls_count = len(url_list)


    #проходжу по кожному посиланню та витягую дані
    for url in url_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # driver = webdriver.Chrome(
        #     executable_path='chromedriver/chromedriver.exe',
        #     options=options
        # )
        # driver.maximize_window()
        #завантажуємо сторінку, щоб витягнути дані про перегляди та місто
        try:
            driver.get(url=url)
            time.sleep(3)
            with open(f'C:/Users/Vadym/Documents/projects/olx_parser/temp_pages/{count}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
            time.sleep(3)
        except Exception as ex:
            print(ex)
        # finally:
        #     driver.close()
        #     driver.quit()

        #views, city, звертаємось до завантаженої сторінки
        try:
            with open(f'C:/Users/Vadym/Documents/projects/olx_parser/temp_pages/{count}.html', 'r', encoding='utf-8') as file:
                src = file.read()
            soup_temp = BeautifulSoup(src, "lxml")
            item_views = soup_temp.find("span", {"data-testid": "page-view-text"}).text[11:].strip()
            item_city = soup_temp.find("p", {"class": "css-7xdcwc-Text eu5v0x0"}).text[:-2]
        except Exception as _ex:
            print(_ex)
        print(item_views)
        print(item_city)

        #name
        try:
            item_name = soup.find("h1", {"data-cy": "ad_title"}).text.strip()
        except Exception as _ex:
            item_name = None
        print(item_name)

        # price
        try:
            item_price = soup.find("h3", {"class": "css-okktvh-Text eu5v0x0"}).text.strip()
        except Exception as _ex:
            item_price = None
        print(item_price)

        # date of publishing
        try:
            item_pab_date = soup.find("span", {"data-cy": "ad-posted-at"}).text.strip()
        except Exception as _ex:
            item_pab_date = None
        print(item_pab_date)

        #description
        try:
            item_description = soup.find("div", {"class": "css-g5mtbi-Text"}).text.strip()
        except Exception as _ex:
            item_description = None
        print(item_description)

        #id
        try:
            item_id = soup.find("span", {"class": "css-9xy3gn-Text eu5v0x0"}).text[3:].strip()
        except Exception as _ex:
            item_id = None
        print(item_id)

        #negotiations?
        try:
            item_neg = soup.find("p", {"data-testid": "negotiable-label"}).text.strip()
        except Exception as _ex:
            item_neg = None
        print(item_neg)

        #bussines or fiz
        try:
            item_biz_or_fiz = soup.find("p", {"class": "css-xl6fe0-Text eu5v0x0"}).text.strip()
        except Exception as _ex:
            item_biz_or_fiz = None
        print(item_biz_or_fiz)

        #saller name
        try:
            item_saller_name = soup.find("h4", {"class": "css-1rbjef7-Text eu5v0x0"}).text.strip()
        except Exception as _ex:
            item_saller_name = None
        print(item_saller_name)

        #working time
        try:
            item_saller_work_time = soup.find("div", {"class": "css-1we7nzp-Text eu5v0x0"}).text.strip()[13:]
        except Exception as _ex:
            item_saller_work_time = None
        print(item_saller_work_time)

        #item status
        try:
            item_status = soup.find_all("p", {"class": "css-xl6fe0-Text eu5v0x0"})[1].text[5:].strip()
            if item_status == "Б/в":
                item_status = "Б/в"
            elif item_status == "Нові":
                item_status = "Нові"
            else:
                item_status = "Не вказано"
        except Exception as _ex:
            item_saller_s_del = None
        print(item_status)

        #словник для збереження всіх даних
        result_dict = {}

        result_dict["item_name"] = item_name
        result_dict["item_url"] = url
        result_dict["item_city"] = item_city
        result_dict["item_price"] = item_price
        result_dict["item_pablishing_date"] = item_pab_date
        result_dict["item_status"] = item_status
        result_dict["item_description"] = item_description
        result_dict["item_id"] = item_id
        result_dict["item_negotiations"] = item_neg
        result_dict["item_views"] = item_views
        result_dict["item_biz_or_fiz"] = item_biz_or_fiz
        result_dict["item_saller_name"] = item_saller_name
        result_dict["item_saller_work_time"] = item_saller_work_time

        #словник додаю до результуючого списку
        result_list.append(result_dict)
        print(result_dict)

        print(f"[+] Processed: {count}/{urls_count}")
        
        #роблю рандомні паузі, щоб не заблокував сайт мій бот
        time.sleep(random.randrange(3, 6))
        if count%10 == 0:
            time.sleep(random.randrange(5, 9))


        count += 1

        #запис даних в .csv файл
        with open("result.csv", "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    item_name,
                    url,
                    item_city,
                    item_price,
                    item_pab_date,
                    item_status,
                    item_description,
                    item_id,
                    item_neg,
                    item_views,
                    item_biz_or_fiz,
                    item_saller_name,
                    item_saller_work_time
                 )
            )
        #запис даних в json файл

        with open("result_json.json", "w", encoding="utf-8") as file:
            json.dump(result_list, file, indent=4, ensure_ascii=False)

        #конвертація csv в xlsx
        df = pd.read_csv("result.csv")
        df.to_excel("result.xlsx", sheet_name=f"Аналіз запиту_{datetime.date.today()}", index=False)

    return "[INFO] Data collected successfully!"



def main():
    #пошук та скачування сторінок з результатами оголошень
    search_text = input("Enter search query: ")
    get_source_html("https://www.olx.ua/", search_text.strip())
    paste_urls_into_txt()



if __name__ == '__main__':
    main()
