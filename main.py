import time
import pathlib
import os
import json
import smtplib
import ssl
from email.message import EmailMessage
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome


def init():
    # Get credentials
    if not os.path.exists(str(pathlib.Path().absolute()) + "/data.json"):
        # if data file does not exist, ask for credentials and create one (only first time)
        cred = dict()
        cred["credentials"] = dict()
        cred["grades"] = dict()
        cred["mail"] = dict()
        cred["credentials"]["username"] = input("Please enter your primuss username: ")
        cred["credentials"]["password"] = input("Please enter your primuss password: ")
        cred["mail"]["address"] = input("Please enter your gmail address from which emails gonna be send to you: ")
        cred["mail"]["password"] = input("Please enter your gmail password: ")

        with open("./data.json", "w") as json_file:
            json.dump(cred, json_file, indent=4, sort_keys=True)

    try:
        # get credentials form data.json file
        with open(str(pathlib.Path().absolute()) + "/data.json") as json_file:
            data = json.load(json_file)
            primuss_username = data["credentials"]["username"]
            primuss_password = data["credentials"]["password"]

    except Exception as e:
        print(e)

    finally:
        return primuss_username, primuss_password


def parse(html_table):
    tmp = dict()
    results = dict()
    try:
        # Parse html table in to a nice dict to work with
        rows = html_table.split('<tr')
        i = 0

        for e in rows:
            tmp[i] = e.split('<td')
            i = i + 1

        special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
        for key in tmp:
            if len(tmp[key]) == 8:
                new_key = tmp[key][3].split('<')[0][1:].translate(special_char_map)
                new_grade = tmp[key][6].translate(special_char_map)
                results[new_key] = new_grade.split('<b>')[1].split('</b>')[0]

    except Exception as e:
        print(e)

    finally:
        return results


def check(results):
    update = False
    try:
        # check whether the grades where updated or not
        with open(str(pathlib.Path().absolute()) + "/data.json", "r+") as json_file:
            data = json.load(json_file)

            if len(data["grades"]) > 0:
                for subject in data["grades"]:
                    if results[subject] != data["grades"][subject]:
                        update = True
                        break
            for subject in results:
                data["grades"][subject] = results[subject]
            json_file.seek(0)
            json.dump(data, json_file, indent=4, sort_keys=True)
            json_file.truncate()

    except Exception as e:
        print(e)

    finally:
        return update


def notify():
    # send an email to the user so he can be happy (... or sad)
    text = 'Your grades have changed! Check them out!\n\n'

    try:
        with open(str(pathlib.Path().absolute()) + "/data.json", "r") as json_file:
            data = json.load(json_file)
            for subject in data["grades"]:
                text = text + subject + ":\n\t--> " + str(data["grades"][subject]) + "\n\n"

            msg = EmailMessage()
            msg.set_content(text)
            msg['Subject'] = 'New Grades!'
            msg['From'] = "Your Friendly Gr(e)at Bot <" + data["mail"]["address"] + ">"
            msg['To'] = data["credentials"]["username"]

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(data["mail"]["address"], data["mail"]["password"])
                server.sendmail(data["mail"]["address"], data["credentials"]["username"]+"@thi.de", msg.as_string())

    except Exception as e:
        print(e)


def main():
    # setup
    primuss_username, primuss_password = init()

    # Start browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = Chrome(options=chrome_options)
    browser.implicitly_wait(10)
    browser.get('https://www3.primuss.de/cgi-bin/login/index.pl?FH=fhin')

    try:
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
        open_menu = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div/div[1]/button')
        open_menu.click()
        my_exams = browser.find_element_by_xpath('//*[@id="nav-prim"]/div/ul/li[4]/a')
        my_exams.click()
        my_grades = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[1]/div[2]/form/input[6]')
        my_grades.click()

        # Get the current grades
        new_grades = browser.find_element_by_xpath('//*[@id="content-body"]/table[2]/tbody[2]').get_attribute('innerHTML')

        # Parse grades from table
        results = parse(new_grades)

        # check for updates
        update = check(results)

        # If grades were updated, send email
        if update:
            notify()

    except Exception as e:
        print(e)

    finally:
        browser.close()


if __name__ == '__main__':
    main()
