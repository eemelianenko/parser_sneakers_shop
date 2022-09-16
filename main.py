import csv
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os


def get_all_pages():
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }

    req = requests.get(url="https://(site).ru/sale/", headers=headers)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/page_1.html", "w", encoding="utf-8") as file:
        file.write(req.text)

    with open("data/page_1.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    pages_count = int(soup.find("div", class_="pagination").find_all("li")[-2].text)

    for i in range(1, pages_count + 1):
        url = f"https://(site).ru/sale/?PAGEN_1={i}"
        req = requests.get(url=url, headers=headers)

        with open(f"data/page_{i}.html", "w", encoding="utf-8") as file:
            file.write(req.text)

        time.sleep(2)

    return pages_count + 1


def collect_data(pages_count):
    data = []

    current_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"sale_data_{current_date}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator='\n')

        writer.writerow(
            (
                "Наименование",
                "Старая цена",
                "Цена со скидкой",
                "Скидка"
            )
        )

    for page in range(1, pages_count):
        with open(f"data/page_{page}.html", encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_cards = soup.find_all("div", class_="product-cards__item")

        for item in items_cards:
            product_title = item.find("a").text.strip()
            product_old_price = item.find("span", class_="product-card__price-value--old").text.strip().replace(" ", " ")
            product_price = item.find_all("span", class_='product-card__price-value')[-1].text.strip().replace(" ", " ")
            product_sale = item.find("span", class_="product-label--discount").text.strip()

            data.append(
                {
                    "product_title": product_title,
                    "product_old_price": product_old_price,
                    "product_price": product_price,
                    "product_sale": product_sale
                }
            )

            with open(f"sale_data_{current_date}.csv", "a", encoding="utf-8") as file:
                writer = csv.writer(file, lineterminator='\n')

                writer.writerow(
                    (
                        product_title,
                        product_old_price,
                        product_price,
                        product_sale
                    )
                )

        print(f"Обработано страниц {page}/{pages_count - 1}")

    with open(f"sale_data_{current_date}.json", "a", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    pages_count = get_all_pages()
    collect_data(pages_count)


if __name__ == "__main__":
    main()
