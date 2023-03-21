from functions import *
import time
from datetime import date

# This code has not been maintained since 09.2022

"""
Script for scraping job postings from LinkedIn using Selenium and BeautifulSoup.
It starts a remote Selenium driver to perform the scraping in a Chrome browser, and then extracts information
from the job postings using BeautifulSoup.
"""


def main(port):
    driver = start_remote_driver(port)
    time.sleep(5)
    reject_cookies(driver)
    time.sleep(3)
    titles_list = [""" "Data" "Analyst" """, """ "Business" "Analyst" """, """ "Marketing" "Analyst" """,
                   """ "Financial" "Analyst" """, """ "Healthcare" "Analyst" """]
    for title in titles_list:
        try:
            reject_cookies(driver)
        except:
            pass
        inputbox(driver,title)
        time.sleep(5)
        checkbox(driver)
# runs scroll_master() function multiple times to make sure everything is loaded.
        scroll_master(driver)
        time.sleep(2)
        scroll_master(driver)
        time.sleep(2)
        scroll_master(driver)

        list = jobs_list(driver)
        repeat_list = []
        collect_jobs(driver,list,repeat_list)
        collet_all_whats_left(repeat_list,driver,list)


        for job in list:
            job.collection_date = date.today().strftime("%d/%m/%Y")
            job.search = title

        data_set = create_data_set(list)
        name = f"""{title} {date.today().strftime("%d_%m_%Y")}"""
        name = name.replace('"','').replace("  "," ")
        save_data_set(data_set,name)