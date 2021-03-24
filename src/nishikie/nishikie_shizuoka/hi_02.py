import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select

# モジュールのインポート
from bs4 import BeautifulSoup

import chromedriver_binary


userDataDir = "/Users/nakamurasatoru/git/d_genji/genji_curation/src/500_common/Chrome3res"
profileDirectory = "Profile 3"


options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir='+userDataDir)
options.add_argument('--profile-directory='+profileDirectory)
driver = webdriver.Chrome(options=options) #, executable_path=driver_path

url = 'https://wwwap.hi.u-tokyo.ac.jp/ships/shipscontroller'

driver.get(url)

driver.find_element_by_link_text("錦絵データベース").click()

Select(driver.find_element_by_name("nitem01")).select_by_value("item06")

driver.find_element_by_name("nterm01_1").send_keys("静岡県立中央図書館")

driver.find_element_by_class_name("btn85").click()

#########

pages = [9, 17, 25, 33, 41, 49, 57, 65, 73]
for page in pages:
    driver.find_element_by_link_text(str(page)).click()

driver.find_element_by_link_text("詳細").click()

flg = True

count = 1

while flg:

    time.sleep(2)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html")

    index = soup.find(class_="res_tbl").find("td").text.split("/")[0]

    name = "data/" + index.zfill(4)+".html"

    with open(name, mode='w') as f:
        f.write(str(soup))

    btns = driver.find_elements_by_class_name("btn85")

    if len(btns) == 0:
        flg = False

    driver.find_elements_by_class_name("btn85")[1].click()

    count += 1

time.sleep(20)

#全てのウィンドウを閉じる
driver.quit()