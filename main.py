from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

options = Options()
options.headless = True  # без окна, если хочешь
driver = webdriver.Chrome(options=options)  # скачай chromedriver под свою версию Chrome

url = "https://www.ic.gc.ca/app/scr/tds/web/list-liste?lang=eng"
driver.get(url)

# Если нужно запустить поиск — найди кнопку и кликни
try:
    search_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], [value='Search']"))
    )
    search_btn.click()
except:
    print("Поиск не нужен или кнопка не найдена — продолжаем")

all_data = []
page = 1
max_pages = 313  # примерно, можно динамически проверять

while page <= max_pages:
    try:
        # Ждём загрузки таблицы
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result_table"))
            # или By.CLASS_NAME "resultTable", подгони по инспектору
        )

        # Извлекаем строки
        rows = driver.find_elements(By.CSS_SELECTOR, "#result_table tr")  # подгони селектор!
        for row in rows[1:]:  # пропустить заголовок
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                name_elem = cols[0].find_element(By.TAG_NAME, "a")
                name = name_elem.text.strip()
                link = name_elem.get_attribute("href")
                address = cols[1].text.strip()

                # Чтобы взять полный телефон/email — нужно открыть ссылку (это сильно замедлит!)
                # driver2 = webdriver.Chrome(); driver2.get(link); ... extract ... driver2.quit()
                # Или просто сохраняем то, что есть

                all_data.append([name, address, link])  # + phone, email если откроешь

        print(f"Страница {page} — собрано {len(all_data)} записей")

        # Переход на следующую
        try:
            next_btn = driver.find_element(By.LINK_TEXT, "Next")  # или CSS [aria-label="Next"]
            if "disabled" in next_btn.get_attribute("class") or not next_btn.is_enabled():
                break
            next_btn.click()
            time.sleep(3)  # анти-бан
            page += 1
        except:
            break

    except Exception as e:
        print(f"Ошибка на странице {page}: {e}")
        break

driver.quit()

# Сохраняем
with open('lit_list_basic.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Address', 'Detail_Link'])
    writer.writerows(all_data)

print(f"Готово! Собрано {len(all_data)} базовых записей.")