from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import pandas as pd


def start_remote_service():
    """
     Starts a remote service using chromedriver.Creates a service object, starts the service and prints the port number being used.
     Returns the service object. This function should be started in a separate terminal to prevent the Ctrl+C shortcut from closing the webdriver.
     """
    path = "C:\Program Files (x86)\chromedriver.exe"
    service = Service(path)
    service.start()
    print(service.port)
    return service


def start_remote_driver(port):
    """
    Starts a remote driver by creating a new instance of a webdriver object, using service provided by start_remote_service() function.
    It takes a port number as an argument and uses it to connect to the remote webdriver server.
    Then it maximizes the window and navigates to a specific URL on the LinkedIn job search page.
    Returns the webdriver object.
    """
    driver = webdriver.Remote(f"http://127.0.0.1:{port}", desired_capabilities=webdriver.DesiredCapabilities.CHROME)
    driver.maximize_window()
    driver.get(
        "https://ie.linkedin.com/jobs/search?keywords=&location=Ireland&geoId=104738515&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")
    return driver


# reject_cookies; inputbox, checkbox create a group of functions responsible for selecting the appropriate search parameters.

def reject_cookies(driver):
    """
     This function clicks the primary button to reject cookies.
     It takes a webdriver object as an argument.
     """
    button = driver.find_element_by_class_name("artdeco-button--primary")
    button.click()

def inputbox(driver,text):
    """
    This function clears the input box, types the given text and clicks the search button.
    It takes a webdriver object and the text to be searched as arguments.
    """
    input_box = driver.find_element_by_xpath("//html/body/div[1]/header/nav/section/section[2]/form/section[1]/input")
    input_box.clear()
    input_box.send_keys(text)
    # search_box = driver.find_element_by_xpath("/html/body/div[1]/header/nav/section/section[2]/form/button/icon/svg/path")
    search_box = driver.find_element_by_xpath("//html/body/div[1]/header/nav/section/section[2]/form/button/icon")
    search_box.click()

def checkbox(driver):
    """
    This function selects the checkbox for internship and entry-level jobs.
    It takes a webdriver object as an argument and locates given checkboxes and marks them
    """
    check_box= driver.find_element_by_xpath("""//*[@id="jserp-filters"]/ul/li[5]/div/div/button""")
    try:
        intership_box = driver.find_element_by_xpath("""//*[@id="jserp-filters"]/ul/li[5]/div/div/div/div/div/div[1]""")
    except:
        pass
    try:
        entry_level_box = driver.find_element_by_xpath("""//*[@id="jserp-filters"]/ul/li[5]/div/div/div/div/div/div[2]""")
    except:
        pass
    done_box = driver.find_element_by_xpath("""//*[@id="jserp-filters"]/ul/li[5]/div/div/div/button""")
    try:
        check_box.click()
        time.sleep(1)
        intership_box.click()
        entry_level_box.click()
        done_box.click()
    except:
        print("Error")


def scroll_master(driver):
    """
    Scrolls through the webpage and loads all the results by clicking on the "See More Results" button when it appears.
    It does this by repeatedly scrolling to the bottom of the page and checking if the page height has increased.
    If the height does not increase, it waits for 5 seconds and then scrolls again to ensure that the "See More Results" button is loaded.
    Once all the results are loaded, it returns the driver to the top of the page to begin the actual web scraping process.
    Takes driver as an argument.
    """
    action_chains = ActionChains(driver)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            see_more_results = driver.find_element_by_class_name("infinite-scroller__show-more-button--visible")
            action_chains.move_to_element(see_more_results).move_by_offset(175, 0).click().perform()
        except:
            pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                try:
                    see_more_results = driver.find_element_by_class_name("infinite-scroller__show-more-button--visible")
                    action_chains.move_to_element(see_more_results).move_by_offset(175, 0).click().perform()
                except:
                    pass
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                extra_new_height = driver.execute_script("return document.body.scrollHeight")
                if extra_new_height == last_height:
                    break
        last_height = new_height
    driver.execute_script("window.scrollTo(0,0);")


def jobs_list(driver):
    """
    Makes list of all jobs and return it.
    Takes driver as an argument.
    """
    jobs_list=[]
    jobs = driver.find_elements_by_tag_name("li")
    for i in jobs:
        try:
            i.find_element_by_class_name("base-search-card__info").text
            jobs_list.append(i)
        except:
            pass
    return jobs_list


def description_key_words(job, description):
    # Get the text of the job description and convert to lowercase
    description_text = description[0].get_text(separator=' ').lower()

    # Replace certain characters with a space
    signs = [".", ",", ";", "!", "?", "/"]
    for sign in signs:
        description_text = description_text.replace(sign, " ")

    # Create a list of keywords to look for in the job description
    key_words_list = ["sql", " python ", " excel ", " r ", " tableau ", " power bi "]

    # Check if each keyword is in the job description, and set the attribute value for that keyword in the job object
    for word in key_words_list:
        if word in description_text:
            job.__setattr__(word, 1)
        else:
            job.__setattr__(word, 0)


def get_job_attributes(driver, jobs_list, job,repeat_list):
    """
    This function extracts job attributes from a job listing on LinkedIn using BeautifulSoup and Selenium.

    Args:
    - driver: Selenium WebDriver object
    - jobs_list: list of job listing elements on the current page
    - job: the job listing element for which to extract attributes
    - repeat_list: list of job listings that need to be repeated (i.e., could not be processed successfully)
    """
    index = jobs_list.index(job)
    try:
        jobs_list[index+1].click()
    except:
        pass
    try:
        jobs_list[index].click()
    except:
        try:
            height = jobs_list[index].location['y']
            driver.execute_script(f"window.scrollTo(0,{height - 234} );")
            jobs_list[index].click()
        except:
            repeat_list.append(job)
            print("added to repeat list")
            print(len(repeat_list))
    time.sleep(0.75)
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    top = soup.find_all('div', {"class": "babybear:w-full"})
    position_name = job.find_element_by_tag_name('h3').text.replace('\n', ' ').strip()
    company_name = job.find_element_by_tag_name('h4').text.replace('\n', ' ').strip()
    try:
        position_name_check = top[0].find_all('h2', {"class": "topcard__title"})[0].text.replace('\n', ' ').strip()
        company_name_check = top[0].find_all('span', {"class": "topcard__flavor"})[0].text.replace('\n',
                                                                                                            ' ').strip()
        if position_name.replace(" ","") == position_name_check.replace(" ","") and company_name.replace(" ","") == company_name_check.replace(" ",""):
            job.position_name = position_name
            job.company_name = company_name
            job.job_location = top[0].find_all('span', {"class": "topcard__flavor--bullet"})[0].text.replace('\n',
                                                                                                             ' ').strip()
            try:
                rest = soup.find_all('li',{"class": "description__job-criteria-item"})
                for item in rest:
                    split = item.text.replace('\n', '  ').strip().split("            ")
                    job.__setattr__(split[0].strip(),split[-1].strip())
            except:
                job.check = 1
            description = soup.find_all(dir, {"class": "show-more-less-html__markup"})
            description_key_words(job,description)
        else:
            repeat_list.append(job)

    except:
        repeat_list.append(job)




def repeated_get_job_attributes(driver, jobs_list, job,repeat_list):

    """
    This function job is analogous to function get_job_attributes() but procedures with job from repeat_list. Job is deleted from list if successfully collected.
    """
    index = jobs_list.index(job)
    try:
        jobs_list[index+1].click()
    except:
        pass
    try:
        jobs_list[index].click()
    except:

        try:
            height = jobs_list[index].location['y']
            driver.execute_script(f"window.scrollTo(0,{height - 234} );")
            jobs_list[index].click()

        except:
            print("job is staying on repeat list")
            print(len(repeat_list))

    time.sleep(0.75)
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    top = soup.find_all('div', {"class": "babybear:w-full"})
    position_name = job.find_element_by_tag_name('h3').text.replace('\n', ' ').strip()
    company_name = job.find_element_by_tag_name('h4').text.replace('\n', ' ').strip()
    try:
        position_name_check = top[0].find_all('h2', {"class": "topcard__title"})[0].text.replace('\n', ' ').strip()
        company_name_check = top[0].find_all('span', {"class": "topcard__flavor"})[0].text.replace('\n',
                                                                                                            ' ').strip()
        if position_name.replace(" ","") == position_name_check.replace(" ","") and company_name.replace(" ","") == company_name_check.replace(" ",""):
            job.position_name = position_name
            job.company_name = company_name
            job.job_location = top[0].find_all('span', {"class": "topcard__flavor--bullet"})[0].text.replace('\n',
                                                                                                             ' ').strip()
            try:
                rest = soup.find_all('li',{"class": "description__job-criteria-item"})
                for item in rest:
                    split = item.text.replace('\n', '  ').strip().split("            ")
                    job.__setattr__(split[0].strip(),split[-1].strip())
                print("7")
            except:
                job.check = 1

            description = soup.find_all(dir, {"class": "show-more-less-html__markup"})
            description_key_words(job,description)
            repeat_list.remove(job)
        else:
            print("job is staying on repeat list")
            print(len(repeat_list))
            print(f"""pno: {position_name.replace(" ","")}""")
            print(f"""pnc: {position_name_check.replace(" ","")}""")
            print(f"""cno: {company_name.replace(" ","")}""")
            print(f"""cnc: {company_name_check.replace(" ","")}""")
    except:
        print("job is staying on repeat list")
        print(len(repeat_list))


def collect_jobs(driver,list,repeat_list):
    """
    Runs get_job_attributes throw all jobs from list
    """
    start_time = time.perf_counter()
    i=1
    for job in list:
        print(f"oferta numer: {i}, czas od poczatku trawania programu: {time.perf_counter() - start_time}")
        get_job_attributes(driver,list,job,repeat_list)
        i=i+1



def collet_jobs_left(driver,list,repeat_list):
    """
    Runs repeated_get_job_attributes throw all jobs from repeat_list
    """
    start_time = time.perf_counter()
    i=1
    for job in repeat_list:
        print(f"oferta numer: {i}, czas od poczatku trawania programu: {time.perf_counter() - start_time}")
        repeated_get_job_attributes(driver,list,job,repeat_list)
        i=i+1


def collet_all_whats_left(repeat_list, driver, list):
        while not len(repeat_list) == 0:
            collet_jobs_left(driver, list, repeat_list)


def create_data_set(list):
    """
    This function creates pandas DataFrame object from collected jobs data.
    :param list:
    :return:
    """
    keys_list=['position_name', 'company_name', 'job_location','Seniority level', 'Employment type', 'Job function', 'Industries', "sql", " python ", " excel ", " r "," tableau "," power bi ","collection_date","search"]
    data=[]
    for job in list:
        att_list =[]
        for key in keys_list:
            try:
                att_list.append(job.__dict__[key])
            except:
                att_list.append('N/a')
        data.append(att_list)

    df = pd.DataFrame(data,columns = keys_list)
    return df

def save_data_set(data_set,name):
    data_set.to_csv(f'{name}.csv')
