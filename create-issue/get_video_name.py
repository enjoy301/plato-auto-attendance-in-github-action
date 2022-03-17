import yaml
import os
import time
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class CheckLectures:
    def __init__(self):
        self.videos = list()
        self.student_number = None
        self.password = None
        self.config = None
        self.driver = None
        self.options = None

    def set_chromedriver_option(self):
        self.options = webdriver.ChromeOptions()
        options = self.options
        options.add_argument('window-size=1920x1080')
        options.add_argument("-start-maximized")
        options.add_argument("--headless")
        options.add_argument("--disable-notifications")

    def get_driver_instance(self):
        s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=s, options=self.options)
        self.driver.implicitly_wait(5)

    def get_user_information(self):
        with open('../secrets.yml', encoding='UTF8') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            self.student_number = config['student-number']
            self.password = config['password']

    def login(self):
        driver = self.driver
        driver.get('https://plato.pusan.ac.kr/')
        driver.find_element(By.ID, "input-username").send_keys()
        driver.find_element(By.ID, "input-username").send_keys(self.student_number)
        driver.find_element(By.ID, "input-password").send_keys(self.password)
        driver.find_element(By.XPATH, '//*[@id="page-header"]/div[1]/div/div[2]/form/div/input[3]').click()
        time.sleep(2)

    def close_popup(self):
        driver = self.driver
        main_page = driver.find_element(By.XPATH, '//*[@id="page-container"]')
        notice_list = main_page.find_elements(By.CSS_SELECTOR, '[class|="modal notice_popup ui-draggable"]')
        z_index_list = []
        for i in notice_list:
            z_index_list.append(i.value_of_css_property("z-index"))

        for _ in range(len(notice_list)):
            max_index = z_index_list.index(max(z_index_list))
            notice_list[max_index].find_element(By.CLASS_NAME, 'close_notice').click()
            z_index_list.pop(max_index)
            notice_list.pop(max_index)
            driver.execute_script("window.scrollTo(0, 0)")

    def check(self):
        time_now = datetime.now() + timedelta(hours=9)

        driver = self.driver
        count_lecture = len(driver.find_elements(By.XPATH, '//*[@id="page-content"]/div/div[1]/div[2]/ul/li'))
        for i in range(1, count_lecture + 1):
            main_page = driver.find_element(By.XPATH, '//*[@id="page-content"]/div/div[1]/div[2]/ul')
            main_page.find_element(By.XPATH, f'./li[{i}]/div/a/div').click()
            time.sleep(1)
            url = "https://plato.pusan.ac.kr/report/ubcompletion/user_progress_a.php?id=" + str(driver.current_url[-6:])
            driver.execute_script(f'window.open("{url}");')
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(0.5)
            main_table = driver.find_element(By.XPATH, '//*[@id="ubcompletion-progress-wrapper"]/div[2]/table/tbody')
            tr_list = main_table.find_elements(By.TAG_NAME, 'tr')
            lecture_list = []
            for lec in tr_list:
                td_list = lec.find_elements(By.TAG_NAME, 'td')
                if len(td_list) == 4:
                    if td_list[3].text == "X":
                        lecture_list.append(td_list[0].text)
                else:
                    if td_list[4].text == "X":
                        lecture_list.append(td_list[1].text)

            time.sleep(0.5)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(0.5)

            if len(lecture_list) == 0:
                driver.get('https://plato.pusan.ac.kr/')
                time.sleep(1)
                continue

            now_index = 0
            # li_list는 1주차부터 16주차까지 block들이 담겨있는 list
            li_list = driver.find_element(By.XPATH, '//*[@id="course-all-sections"]/div/ul').find_elements(By.TAG_NAME, 'li')

            for index, li in enumerate(li_list):
                num = index + 1
                ul_list = li.find_element(By.XPATH, f'//*[@id="section-{num}"]/div[3]').find_elements(By.TAG_NAME, 'ul')
                # "len(ul_list) == 0" 은 그 주차에 아무 강의 자료 없다는 뜻
                if len(ul_list) == 0:
                    continue
                # file 하나하나 탐색
                for file in ul_list[0].find_elements(By.TAG_NAME, 'li'):
                    my_text = file.text
                    if (lecture_list[now_index] in my_text) and ("동영상" in my_text):
                        duration = my_text[my_text.find('동영상') + 5:my_text.find('동영상') + 46]
                        from_d = datetime.strptime(duration[:19], "%Y-%m-%d %H:%M:%S")
                        until_d = datetime.strptime(duration[22:], "%Y-%m-%d %H:%M:%S")

                        # 출석인정기간인 경우
                        if (from_d <= time_now) and (time_now <= until_d):
                            self.videos.append(lecture_list[now_index])

                        now_index += 1

                        if len(lecture_list) == now_index:
                            # 이번 주차의 파일 하나 하나 탐색하는 for문을 break
                            break
                if len(lecture_list) == now_index:
                    # 다음 주차의 블록으로 넘어가지 않는다는 break
                    break

            driver.get('https://plato.pusan.ac.kr/')
            time.sleep(1)

        driver.close()

    def main(self):
        self.set_chromedriver_option()
        self.get_driver_instance()
        self.get_user_information()
        self.login()
        self.close_popup()
        self.check()
