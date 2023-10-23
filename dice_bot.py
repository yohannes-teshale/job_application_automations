from dotenv import load_dotenv
import os
import time
import csv
import sys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains






################## Setting up global variables and configs
load_dotenv()
if len(sys.argv) <= 1:
    exit("You must provide some key words.")

keywords = '%20'.join(sys.argv[1:])

options = Options()
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


def create_csv_file():
    current_date = time.strftime("%Y-%m-%d")
    csv_filename = f"job_applications_{current_date}.csv"

    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Job Title", "Company", "Location", "Job URL"])
    return csv_filename
            
def login_to_dice():
    dice_username= os.getenv('DICE_USERNAME')
    dice_password= os.getenv('DICE_PASSWORD')
    driver.get("https://www.dice.com/dashboard/login")
    driver.find_element(By.ID, "email").send_keys(dice_username)
    driver.find_element(By.ID, "password").send_keys(dice_password)
    driver.find_element(
        By.XPATH, "//button[contains(text(),'Sign In')]"
    ).click() 
def search_for_jobs(max_jobs_to_apply):
    driver.get(f"https://www.dice.com/jobs?q={keywords}%20&location=United%20States&latitude=37.09024&longitude=-95.712891&countryCode=US&locationPrecision=Country&radius=30&radiusUnit=mi&page=1&pageSize={max_jobs_to_apply}&filters.postedDate=ONE&filters.easyApply=true&language=en&eid=S2Q_")

def apply_for_jobs(filename,max_jobs_to_apply):

    job_links = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "card-title-link"))
    )
    num_jobs_applied=0
    for i in range(len(job_links)):
        try:
            
            job_links = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "card-title-link"))
                   )

            
            job_link = job_links[i]
            
            
            print("Applying...")
            action= ActionChains(driver)
            action.move_to_element(job_link).click().perform()
            # job_link.click()
            #swith to new opened tab
            driver.switch_to.window(driver.window_handles[1])
            apply_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.TAG_NAME, "apply-button-wc"))
                )
            time.sleep(2)
            shadow_root_script = """
                    const shadowHost = arguments[0];
                    const shadowRoot = shadowHost.shadowRoot;
                    return shadowRoot.querySelector('p');"""
            shadow_element = driver.execute_script(shadow_root_script, apply_button)
            
            if shadow_element and "Application Submitted" in shadow_element.text:
                #close and come back to search tab
                close_and_open_search_tab(driver)
                continue
            job_details= extract_info_from_page()
            isValid=filter_jobs(job_details.get('job_title'))
            if not isValid:
                #close and come back to search tab
                close_and_open_search_tab(driver)
                continue;      
            apply_button.click()
            print('uploading resume...')      
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next')]"))
            ).click()
            
            print('reviewing application...')
            
            WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next')]"))
                ).click()
            
            print('Application submitted')
            #close and come back to search tab
            close_and_open_search_tab(driver)
            num_jobs_applied += 1
            print(f"Applied for {num_jobs_applied} jobs.")

            WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'eid=qpw')]"))
                ).click()
            save_information_to_csv(filename,job_details)            
        except Exception:
            driver.get(f"https://www.dice.com/jobs?q={keywords}%20&location=United%20States&latitude=37.09024&longitude=-95.712891&countryCode=US&locationPrecision=Country&radius=30&radiusUnit=mi&page=1&pageSize={max_jobs_to_apply}&filters.postedDate=ONE&filters.easyApply=true&language=en&eid=S2Q_")
            continue
            
            
def close_and_open_search_tab(driver):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
def filter_jobs(job_title):
    black_listed_words =[".NET","C#", "SHAREPOINT", "SHARE POINT", "LEAD", "ARCHITECT", "CLEARANCE", "USC","GC","SECRET","TOP","NET","LOCAL","CITIZEN"]

    for i in black_listed_words:
        if i in job_title.upper():
            return False
    return True   
           
def extract_info_from_page():
    job_title = driver.find_element(By.TAG_NAME,'h1').get_attribute('innerHTML')
    company = driver.find_element('xpath', '//*[@id="__next"]/div/main/header/div/div/div[3]/ul/ul[1]/li[1]/a').get_attribute('innerHTML')
    location = driver.find_element('xpath', '//*[@id="__next"]/div/main/header/div/div/div[3]/ul/ul[1]/li[2]').get_attribute('innerHTML')
    job_url= driver.current_url
    return {"job_title": job_title, "company":company,"location":location,"job_url":job_url}
          
def save_information_to_csv(filename,job_details):
    with open(filename, mode="a", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([job_details.get("job_title"), 
                                     job_details.get("company"), 
                                     job_details.get("location"), 
                                     job_details.get("job_url")])
      
 
if __name__=="__main__":
    filename=create_csv_file()
    login_to_dice()
    search_for_jobs(300)
    apply_for_jobs(filename,300)
    driver.quit()
    
  