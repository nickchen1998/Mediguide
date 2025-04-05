import re
import time
import json
import utils
import pathlib
from datetime import datetime
from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

dataset_path = pathlib.Path(__file__).parent / "datasets.json"
with open(dataset_path, "r", encoding="utf-8") as f:
    datasets = json.load(f)

browser = Safari()

for dataset in datasets:
    browser.get(dataset["start_url"])

    symptom_select_menu = browser.find_element(By.CSS_SELECTOR, "select[name='q_type']")
    symptom_list = [tmp.get_attribute("value") for tmp in symptom_select_menu.find_elements(
        By.TAG_NAME, "option") if tmp.get_attribute("value")]

    for symptom in symptom_list:
        browser.get(
            f"https://sp1.hso.mohw.gov.tw/doctor/Often_question/type_detail.php?"
            f"q_type={symptom}&UrlClass={dataset['department']}"
        )
        datas = []
        for paragraph in browser.find_elements(By.CSS_SELECTOR, "ul.QAunit"):
            time.sleep(10)

            subject = paragraph.find_element(By.CSS_SELECTOR, "li.subject").text

            asker_info = paragraph.find_element(By.CSS_SELECTOR, "li.asker").text
            match = re.search(r'／([男女])／.*?,(\d{4}/\d{2}/\d{2})', asker_info)
            gender = match.group(1)
            question_time = datetime.strptime(match.group(2), '%Y/%m/%d')

            question = paragraph.find_element(By.CSS_SELECTOR, "li.ask").text

            answer = paragraph.find_element(By.CSS_SELECTOR, "li.ans").text
            answer_time = datetime.strptime(match.group(2), '%Y/%m/%d')

            data = dict(
                subject_id=int(subject.split(" ")[0].replace("#", "")),
                subject="".join(subject.split(" ")[1:]),
                symptom=symptom,
                question=question,
                gender=gender,
                question_time=question_time,
                answer=answer,
                department=dataset["department"],
                answer_time=answer_time,
            )

            datas.append(data)

            try:
                next_page_element = browser.find_element(By.LINK_TEXT, "下一頁")
                next_page_element.click()
            except NoSuchElementException:
                break
        if datas:
            utils.insert_symptom_subject_datas(datas)

browser.quit()
