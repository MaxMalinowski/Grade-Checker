import time
import os
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome


def init():
    # Get credentials
    if not os.path.exists("./data.json"):
        # if data file does not exist, ask for credentials and create one (only first time) 
        cred = dict()
        cred["credentials"] = dict()
        cred["grades"] = dict()
        cred["credentials"]["username"] = input("Please enter your primuss username: ")
        cred["credentials"]["password"] = input("Please enter your primuss password: ")
        with open("data.json", "w") as json_file:
            json.dump(cred, json_file, indent=4, sort_keys=True)

    # get credentials form data.json file
    with open("./data.json") as json_file:
        data = json.load(json_file)
        primuss_username = data["credentials"]["username"]
        primuss_password = data["credentials"]["password"]

    return primuss_username, primuss_password


def parse(html_table):
    # Parse html table in to a nice dict to work with
    rows = html_table.split('<tr')
    i = 0
    tmp = dict()
    for e in rows:
        tmp[i] = e.split('<td')
        i = i + 1

    results = dict()
    for key in tmp:
        if len(tmp[key]) == 8:
            new_key = tmp[key][3].split('<')[0][1:]
            new_grade = tmp[key][6]
            results[new_key] = new_grade.split('<b>')[1].split('</b>')[0]

    return results

def check(results):
    # check whether the grades where updated or not
    with open("data.json", "r+") as json_file:
        data = json.load(json_file)
        update = False
        if len(data["grades"]) > 0:
            print("checking....")
            for subject in data["grades"]:
                if results[subject] != data["grades"][subject]:
                    update = True
                    break
        for subject in results:
            data["grades"][subject] = results[subject]
        json_file.seek(0)
        json.dump(data, json_file, indent=4, sort_keys=True)
        json_file.truncate()
    return update

def notify():
    # send an email to the user so he can be happy (... or sad)
    # to be done
    return True


def main():
    # setup
    primuss_username, primuss_password = init()

    # Start browser
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")  
    browser = Chrome(options=chrome_options)
    browser.get('https://www3.primuss.de/cgi-bin/login/index.pl?FH=fhin')
    
    # Login in
    username = browser.find_element_by_id("username")
    username.click()
    username.clear()
    username.send_keys(primuss_username)
    password = browser.find_element_by_id("password")
    username.click()
    password.clear()
    password.send_keys(primuss_password)
    button = browser.find_element_by_xpath('/html/body/div/div[5]/form/div[4]/button')
    button.click()

    # Get to grad announcement page
    my_exams = browser.find_element_by_xpath('//*[@id="nav-prim"]/div/ul/li[4]/a')
    my_exams.click()
    my_grades = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[1]/div[2]/form/input[6]')
    my_grades.click()
    time.sleep(5)

    # Get the current grades
    new_grades = browser.find_element_by_xpath('//*[@id="content-body"]/table[2]/tbody[2]').get_attribute('innerHTML')

    # Parse grades from table
    results = parse(new_grades)

    # check for updates
    update = check(results)

    # If grades were updated, send email
    if update:
        notify()

    browser.close()


if __name__ == '__main__':
    main()