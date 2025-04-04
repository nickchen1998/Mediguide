import re
import time
from pprint import pprint
from datetime import datetime
from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

q_type = "噁心"
UrlClass = "肝膽腸胃科"
browser = Safari()
browser.get(f"https://sp1.hso.mohw.gov.tw/doctor/Often_question/type_detail.php?q_type={q_type}&UrlClass={UrlClass}")

symptom_select_menu = browser.find_element(By.CSS_SELECTOR, "select[name='q_type']")
symptom_list = [tmp.get_attribute("value") for tmp in symptom_select_menu.find_elements(
    By.TAG_NAME, "option") if tmp.get_attribute("value") and tmp.get_attribute("value") != "噁心"]

for symptom in symptom_list:
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
            q_type=q_type,
            subject=subject,
            question=question,
            gender=gender,
            question_time=question_time,
            answer=answer,
            department=UrlClass,
            answer_time=answer_time,
        )
        pprint(data)

        try:
            next_page_element = browser.find_element(By.LINK_TEXT, "下一頁")
            next_page_element.click()
        except NoSuchElementException:
            break

    q_type = symptom
    browser.get(f"https://sp1.hso.mohw.gov.tw/doctor/Often_question/type_detail.php?q_type={q_type}&UrlClass={UrlClass}")

browser.quit()
