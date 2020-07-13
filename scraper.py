from selenium import webdriver
from datetime import datetime
import json
import fire
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time

URL = 'https://parivahan.gov.in/rcdlstatus/?pur_cd=101'


#function to fetch data
def fetch_data(dl_no, dob):
    chrome_driver = webdriver.Chrome()
    time.sleep(5)
    chrome_driver.get(URL)
    time.sleep(5)
    dl_box = chrome_driver.find_element_by_css_selector("#form_rcdl\:tf_dlNO")
    dl_box.send_keys(dl_no.upper())

    def date_parser(check_date):
        try:
            date = datetime.strptime(check_date, "%Y-%m-%d")
        except Exception as e:
            print(e)
            print("Date entered is not valid!")
            check_date = input("enter date as dd-mm-yyyy: ")
            date = date_parser(check_date)
        return date
    date = date_parser(dob)
    date_input_box = chrome_driver.find_element_by_id('form_rcdl:tf_dob_input')
    date_input_box.click()
    time.sleep(2)
    month_selector = Select(chrome_driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    value = date.month - 1

    def month_parser(value):
        try:
            month_selector.select_by_value(str(value))
        except Exception as e:
            month = input("Enter a valid month between 01 to 12")
            date = date.replace(month=int(month))
            value = date.month - 1
            month_parser(value)
    month_parser(value)
    year_selector = Select(chrome_driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]'))
    year = date.year

    def year_parser(check_year):
        try:
            year_selector.select_by_visible_text(str(check_year))
        except Exception as e:
            year = input("Enter valid year")
            date = date.replace(year=int(year))
            check_year = date.year
            year_parser(check_year)
    year_parser(year)
    widget_date = chrome_driver.find_element_by_id("ui-datepicker-div")
    cols = widget_date.find_elements_by_tag_name("td")
    for value in cols:
        if str(value.text) == str(date.day):
            value.find_element_by_link_text(str(date.day)).click()
            break

    captcha = chrome_driver.find_element_by_id('form_rcdl:j_idt31:CaptchaID')


    #this function has to be changed accordingly
    def get_captcha():
        code = input("please enter captcha:")
        return code


    captcha.send_keys(get_captcha())
    submit_button = chrome_driver.find_element_by_id("form_rcdl:j_idt42")
    submit_button.click()
    time.sleep(5)

    def landing_page():
        try:
            parser = BeautifulSoup(chrome_driver.page_source, "html.parser")
            first_table = parser.find("table", {"class", "table table-responsive table-striped table-condensed table-bordered"})
            if first_table is not None:
                sec_table = parser.find("table", {"class", "table table-responsive table-striped table-condensed table-bordered data-table"})
                third_table = parser.find("div", {"class", "ui-datatable-tablewrapper"})
                column_value = third_table.find("tr", {"class", "ui-widget-content ui-datatable-even"})
                licence_details = {}
                for index, value in enumerate(first_table.find_all("td")):
                    if index == 3:
                        licence_details["name"] = value.get_text()
                    elif index == 5:
                        licence_details["date_of_issue"] = value.get_text()
                    else:
                        pass

                for index, value in enumerate(sec_table.tr.find_all("td")):
                    if index == 2:
                        licence_details["date_of_expiry"] = value.get_text()[3:]

                for ins, value in enumerate(column_value.find_all("td")):
                    if ins == 1:
                        licence_details["class_of_vehicle"] = value.get_text()

                json_object = json.dumps(licence_details, indent=4)
                return(json_object)
            elif chrome_driver.find_element_by_xpath('//*[@id="primefacesmessagedlg"]/div[1]/a/span') is not None:
                print("please enter valid details: Eg: avoid using space in licence number")
            elif chrome_driver.find_element_by_xpath('//*[@id="form_rcdl:j_idt13"]/div/ul/li/span[1]') is not None:
                code = input("re-enter captcha")
                captcha_data.send_keys(code)
                button.click()
                time.sleep(5)
            else:
                pass

        except Exception as e:
            print("error:",e)
    return(landing_page())
    chrome_driver.quit()

if __name__ == "__main__":
    fire.Fire(fetch_data)
