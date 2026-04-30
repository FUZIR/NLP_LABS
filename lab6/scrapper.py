import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

SITE_CONFIGS = {
    "rozetka": {
        "pagination": lambda url, page: f"{url}page={page}/" if page > 1 else url,
        "card": (By.TAG_NAME, "rz-product-tile"),
        "title": (By.CSS_SELECTOR, "a.tile-title"),
        "link": (By.CSS_SELECTOR, "a.tile-title"),
        "price_primary": (By.TAG_NAME, "rz-tile-red-price"),
        "price_secondary": (By.TAG_NAME, "rz-tile-price"),
        "price_cleanup": lambda p: p.replace('\xa0', '').replace('₴', '').strip()
    },
    "comfy": {
        "pagination": lambda url, page: f"{url}?p={page}" if page > 1 else url,
        "card": (By.CSS_SELECTOR, "div.product-tile-catalog"),
        "title": (By.CSS_SELECTOR, "div.product-tile-title"),
        "link": (By.CSS_SELECTOR, "a.product-tile-title__name"),
        "price_primary": (By.CSS_SELECTOR, "div.product-tile-price__current"),
        "price_secondary": None,
        "price_cleanup": lambda p: p.replace('\xa0', '').replace('₴', '').replace(' ', '').strip()
    },
    "allo": {
        "pagination": lambda url, page: (
            f"{url}p-{page}/" if url.endswith('/') else f"{url}/p-{page}/") if page > 1 else url,
        "card": (By.CSS_SELECTOR, "div.product-card"),
        "title": (By.CSS_SELECTOR, "a.product-card__title"),
        "link": (By.CSS_SELECTOR, "a.product-card__title"),
        "price_primary": (By.CSS_SELECTOR, "div.v-pb__cur span.sum"),
        "price_secondary": (By.CSS_SELECTOR, "span.sum"),
        "price_cleanup": lambda p: p.replace('\xa0', '').replace(' ', '').strip()
    }
}


def scrape_category(site, url, category_name, output_filename, max_pages=1):
    config = SITE_CONFIGS.get(site)
    if not config:
        print(f"Конфігурація для сайту '{site}' не знайдена.")
        return

    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")

    print(f"\nЗапуск браузера для {site.capitalize()} ({category_name})...")
    driver = uc.Chrome(options=options)
    all_products = []

    try:
        for page in range(1, max_pages + 1):
            page_url = config["pagination"](url, page)
            print(f"Парсинг сторінки {site.capitalize()} {page}: {page_url}")
            driver.get(page_url)

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(config["card"])
                )
            except TimeoutException:
                print(f"Помилка: Товари не знайдені. Зберігаю скріншот 'error_{site}.png'...")
                driver.save_screenshot(f"error_{site}.png")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            product_cards = driver.find_elements(*config["card"])

            for card in product_cards:
                try:
                    title = card.find_element(*config["title"]).text.strip()
                    link = card.find_element(*config["link"]).get_attribute("href")

                    price = "Немає в наявності"
                    try:
                        price_elem = card.find_element(*config["price_primary"])
                        price = config["price_cleanup"](price_elem.text)
                    except:
                        if config["price_secondary"]:
                            try:
                                price_elem = card.find_element(*config["price_secondary"])
                                price = config["price_cleanup"](price_elem.text)
                            except:
                                pass

                    all_products.append({
                        "category": category_name,
                        "title": title,
                        "price": price,
                        "link": link
                    })
                except Exception:
                    continue

            print(f"Зібрано товарів на сторінці: {len(product_cards)}.")
            time.sleep(4)

    finally:
        driver.quit()

    if all_products:
        with open(output_filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["category", "title", "price", "link"])
            writer.writeheader()
            writer.writerows(all_products)
        print(f"Успішно збережено {len(all_products)} товарів у файл {output_filename}")


if __name__ == "__main__":
    urls = {
        "rozetka": {
            "laptops": "https://rozetka.com.ua/ua/notebooks/c80004/",
            "fridges": "https://bt.rozetka.com.ua/ua/refrigerators/c80125/",
            "tvs": "https://rozetka.com.ua/ua/all-tv/c80037/"
        },
        "comfy": {
            "laptops": "https://comfy.ua/ua/notebook/",
            "fridges": "https://comfy.ua/ua/refrigerator/",
            "tvs": "https://comfy.ua/ua/flat-tvs/"
        },
        "allo": {
            "laptops": "https://allo.ua/ua/products/notebooks/",
            "fridges": "https://allo.ua/ua/holodilniki/",
            "tvs": "https://allo.ua/ua/televizory/"
        }
    }

    scrape_category("rozetka", urls["rozetka"]["laptops"], "Комп'ютерна техніка", "rozetka_computers.csv", max_pages=10)
    scrape_category("rozetka", urls["rozetka"]["fridges"], "Холодильники", "rozetka_fridges.csv", max_pages=10)
    scrape_category("rozetka", urls["rozetka"]["tvs"], "Телевізори", "rozetka_tvs.csv", max_pages=10)

    scrape_category("comfy", urls["comfy"]["laptops"], "Комп'ютерна техніка", "comfy_computers.csv", max_pages=10)
    scrape_category("comfy", urls["comfy"]["fridges"], "Холодильники", "comfy_fridges.csv", max_pages=10)
    scrape_category("comfy", urls["comfy"]["tvs"], "Телевізори", "comfy_tvs.csv", max_pages=10)

    scrape_category("allo", urls["allo"]["laptops"], "Комп'ютерна техніка", "allo_computers.csv", max_pages=10)
    scrape_category("allo", urls["allo"]["fridges"], "Холодильники", "allo_fridges.csv", max_pages=10)
    scrape_category("allo", urls["allo"]["tvs"], "Телевізори", "allo_tvs.csv", max_pages=10)
