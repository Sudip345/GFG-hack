import threading
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from collections import deque
import time
import json
import smtplib
from datetime import datetime
import requests
import winsound


solved = False
answer = None


class api_key_exception(Exception):
    pass



def make_beep():
    winsound.Beep(600,1000)
    winsound.Beep(400,1000)
    winsound.Beep(350,1000)


def is_online(url):
    try:
        requests.get(url, timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def send_mail(mail_subject,mail_content,receiver="sudipbag035@gmail.com"):

    try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                sender_email = "sudipbag035@gmail.com"
                app_password = "qeej ktnm mvdq wdag"  # Replace with app password
                server.login(sender_email, app_password)
                msg = f"Subject: {mail_subject}\n\n{mail_content}"
                server.sendmail(sender_email, receiver, msg)
                print("Mail sent successfully.")
                return True
    except Exception as ex:
                print(f"An error occurred: {ex}")
                return False


def handle_submission_error(driver):
    while True:
        try:
            ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']"))
            )
            driver.execute_script("arguments[0].click();", ok_button)  
        except Exception as e:
            pass



def fetch_error(driver):
    try:
        # waiting for the result class to be visible
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "problems_compile_result__2w2iF"))
        )
        
        # Get the element
        result_element = driver.find_element(By.CLASS_NAME, "problems_compile_result__2w2iF")
        
        # Make sure it's visible in the viewport
        driver.execute_script("arguments[0].scrollIntoView(true);", result_element)
        time.sleep(0.7)
        # Get the text content
        msg = result_element.text
        # print(msg)
        
        return msg
        
    except Exception as ex:
        pass



def select_language(driver,lan = 2):

    select = driver.find_element(By.XPATH,"//div[@role= 'listbox']")
    select.click()
    time.sleep(1)
    lan_dict = {1:"C++ (g++ 5.4)",2:"Python3",3:"Java (1.8)",4:"C (gcc 5.4)",5:"Javascript (Node v12.19.0)"}
    
    try:
          
        lan_option = driver.find_element(By.XPATH, f"//div[@class='visible menu transition']//div[@role='option']//span[text()='{lan_dict.get(lan)}']")
        driver.execute_script("arguments[0].scrollIntoView(true);", lan_option)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", lan_option)
        return lan_dict.get(lan)
    except Exception as e:
        # print(f"Failed to select Python3: {e}")
        try:
            lan_option = driver.find_element(By.XPATH, f"//div[@class='item' and .//span[text()='{lan_dict.get(lan)}']]")
            driver.execute_script("arguments[0].click();", lan_option)
            return lan_dict.get(lan)
        except Exception as e2: 
            lan_option = driver.find_element(By.XPATH, f"//div[@class='visible menu transition']//div[@role='option']")
            driver.execute_script("arguments[0].click();", lan_option)
            str= lan_option.text
            return str






def clear_editor(code, driver,lan):
    safe_code = json.dumps(code)
    marker_1 ="driver code starts" 
    marker_2 ="driver code ends"
    js_script = f"""
        var editor = ace.edit(document.querySelector('.ace_editor'));
        var session = editor.getSession();
        var lines = session.getDocument().getAllLines();

        let driverStartIndexes = [];
        let driverEndIndexes = [];

        for (let i = 0; i < lines.length; i++) {{
            if (lines[i].toLowerCase().includes("{marker_1}")) {{
                driverStartIndexes.push(i);
            }}
            if (lines[i].toLowerCase().includes("{marker_2}")) {{
                driverEndIndexes.push(i);
            }}
        }}

        if (driverStartIndexes.length === 0 || driverEndIndexes.length === 0) {{
            alert("No driver code markers found.");
        }} else {{
       
            let logicStart = 0;
            let logicEnd = 0;

            // If there's a second driver block after logic
            if (driverStartIndexes.length > 1 || driverEndIndexes.length>1 ) {{
                logicStart = driverEndIndexes[0]+1;
                logicEnd = driverStartIndexes[1];
            }}
            else {{
                if( driverEndIndexes[0] == lines.length-1){{
                    logicStart = 0;
                    logicEnd = driverStartIndexes[0];
                }}
                else {{
                    logicStart = driverEndIndexes[0]+1;
                    logicEnd = lines.length
                }}
               
            }}

            session.replace({{
                start: {{ row: logicStart, column: 0 }},
                end: {{ row: logicEnd, column: 0 }}
            }}, {safe_code}+"\\n");

            editor.moveCursorTo(logicStart, 0);
        }}
    """
    driver.execute_script(js_script)



def submisson(driver):
        t1 = threading.Thread(target=handle_submission_error,args=(driver,),daemon= True)
        t1.start()
        submit = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,".ui.button.problems_submit_button__6QoNQ"))
        )
        driver.execute_script("""arguments[0].scrollIntoView(true);
                                 arguments[0].click()""",submit )
        
        try:
            solved = WebDriverWait(driver,25).until(
            EC.presence_of_element_located((By.CLASS_NAME,"problems_problem_solved_successfully__Zb4yG"))
            )
            return True
        except Exception:
            print("Not submitted")
            return False
        




def get_response(driver, question, code_snippet, cir_queue, uname,lan=None):
    global solved
    global answer
    submit = None
    if not solved:
        attempt = 0
        message = ""
        
        while attempt < 6:
            your_api_key = cir_queue[0] 
            try:
                client = OpenAI(
                    base_url="https://api.aimlapi.com/v1",
                    api_key=your_api_key,  
                )

                # Determine if this is initial attempt or retry
                if attempt == 0:
                    content = f"""response back the answer only, not anything rather than the solution (in {lan}) no need to include any header file also, 
                    just complete the code snippet, write the code like you are directly writing into the editor, no need to add any special character or mention language name"
                    always write the solution in Solution Class, if selected language supports OOPS concept. give the optimum solution as the constraints are high.
                    follow these strictly.
                    problem statement : {question}
                    code snippet : {code_snippet}"""
                else:
                    error_msg = fetch_error(driver)
                    content = f"""There was a problem with the previous code, write a new one.
                    response back the answer only, not anything rather than the solution (in {lan}). no need to include any header file also, 
                    just complete the code snippet, write the code like you are directly writing into the editor, no need to add any special character or mention language name,
                    always write the solution in "Solution Class" if selected language supports OOPS concept. give the optimum solution as the constraints are high.
                    follow these strictly.
                    previous error : {error_msg}
                    problem statement : {question}
                    code snippet : {code_snippet}"""

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI assistant who knows everything.",
                        },
                        {
                            "role": "user",
                            "content": content
                        },
                    ],
                )
                
                message = response.choices[0].message.content + "\n"
                error_list = ["```", f"java\n", f"cpp\n", f"python\n", f"c\n", f"javascript\n"]
                for items in error_list:
                    message = message.replace(items, "")
                answer = message
                clear_editor(answer, driver, lan)

                submit = submisson(driver)
                if submit:
                    break  # Exit loop if submission succeeds
                    
            except Exception as ex:
                print(f"API key {your_api_key} failed , switching to new one ")
                cir_queue.append(your_api_key)  # Rotate to next API key
                time.sleep(1)  # Add delay before retry
                raise api_key_exception
                
            attempt += 1
    else:
        try:
            clear_editor(answer, driver, lan)
            submit = submisson(driver)
        except Exception as ex :
            pass

    if submit :
        solved = True
        mail_subject = "Prblem solved successfully for today"
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        mail_content =  f"Problem solved successfully on {date}"
        print("Solved")
    else :
        mail_subject = "Could not solve today's problem"
        mail_content = "Failed to solve today's problem"
        print("Not solved")

    send_mail(mail_subject,mail_content,uname)
    # driver.quit()
    # exit(0)


def fetch_code_snip(driver):
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.CLASS_NAME,"ace_line"))
    )
    time.sleep(0.6)
    code_snip = driver.find_elements(By.CLASS_NAME,"ace_line")
    temp=""
    for line in code_snip:
        if "driver code ends" not in line.text.strip().lower():
            temp+=line.text.strip()
            temp+='\n'
    return temp

def fetch_content(driver):
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.TAG_NAME,"p"))
    )
    content = driver.find_elements(By.TAG_NAME,"p")
    question=""
    for str in content:
        if "Example"   not in str.text and "Constraint" not in str.text:
            question+=str.text
    question.replace(' ','')
    return question



def skip_intro(driver):
    try:
        skip_btn =  WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.CLASS_NAME,"potdTour_skip_btn__Ro7RO"))
        )
        skip_btn.click()
 
    except Exception as ex :
        print("skip button not found")
        pass
     


def handle_potd(driver,cir_queue,uname):

    solve_button = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.ID,"potd_solve_prob"))
    )
    solve_button.click()
    time.sleep(2)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])

    question =  fetch_content(driver)
    code_snip = fetch_code_snip(driver)
    language =  select_language(driver,1)
    get_response(driver,question,code_snip,cir_queue,uname,1)
   




def log_in_first(driver,uname,password_):
    msg = ""
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "gfg_loginModalBtn"))
            )
        sign_in_button.click()

        user_name =  WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".mb15.next_input.loginInput.noIconInput"))
            )
        user_name.send_keys(uname)
        user_name.send_keys(Keys.RETURN)
        password= WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password'][placeholder='Enter password']"))
            )
        password.send_keys(password_)
        password.send_keys(Keys.RETURN)

        submit =  WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".loginBtn.btnGreen.notSocialAuthBtn"))
            )
        time.sleep(0.5)
        submit.click()
        time.sleep(6)
      
    except Exception:
        print('Wrong login credentials')
        driver.quit()
        




def accept_cookies(driver):
    try:
        cookies = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.CLASS_NAME,"cookieConsent_gfg_cookie__button__y3NOr"))
        )
        cookies.click()
    except Exception:
        pass


if __name__ == "__main__":

    url = "https://www.geeksforgeeks.org/problem-of-the-day"
    if not is_online(url):
        print("you are offline , exiting....")
        make_beep()
        exit(1)

    api_list =     [
                    "6355687b7910438a8c96955310781383",
                    "8d70b74aa51b40d28968cfcc42f1ca46",
                    "d58d055545104a4e93dedc4356635cc2",
                    "78309b8e9dfd4ad885b5949a8d2159f9",
                    "7ae73d7f86c94b2a84c6ef39685860ec",
                    "bb71e041180940b3928460b6a6884ba1",		
                    "b9611bb1dd7b4e1b972332538a82a009",		
                    "66bf3db4bd1b485b9102ca2e5b338280",		
                    "dcfcb8dc2cc049acb2ea815fb45234a7",		
                    "8e59de218dc64df9a65559cc16968ab9",		
                    "fef381bb22b7409aa5a3e3b2f0d8f5dc",		
                    "ff737be46120433fba0e42fd08100e67",	
                    "dbc78fd1681048599116ba9d88368956",		
                    "88a9c9d0b30e4d87ad4ccc6a60ac5841",
                    "acd82ce1888844fa8e0bb5b5fe8b1a7d",
                    "3895949de5d64c54aaaa6dbf23638601",
                    "787ee0f32a4d4467be0b78dc0455bb4b",
                    "6caf4e03e82b4e2cb59024dda80983cd",
                    "708b34fa11f844e7bb75428722a51e3b",
                    "7979ab47a681408dba5f3eedf552766f",
                    "c99d4f2a97cc478aa42b0f98cefe2a16",
                    "220ca7d1769d4ff7b695f6eb6b1f4eae",
                    "90c66b0f029e4eb0948ae90cb9bd9e4d",
                    "0453c2a2807144bbaafe4434fe8c43a5",
                    "39af475ee06f43d78a3987b6d227d471",
                    "954f1256ab5d46739ad93b9ad06640c8"
                    ]

    cir_queue = deque(api_list,maxlen=len(api_list))
  

    accounts = { "sudipbag157@gmail.com":"Sudip@123",
                 "sudipbag035@gmail.com":'Sudip@123',
                 "araj82537@gmail.com":'Alok@123'}
    
    account_queue = deque(accounts,maxlen=len(accounts))

    seen = set()
    
    while len(seen) != len(account_queue):
        account = account_queue[0]
        if not account in seen:
            driver =  webdriver.Chrome()
            try:
                driver.maximize_window()
                driver.get(url)
                log_in_first(driver,account,accounts.get(account))
                skip_intro(driver)
                accept_cookies(driver)
                try:
                    handle_potd(driver,cir_queue,account)
                    time.sleep(3)
                    seen.add(account)
                    account_queue.append(account_queue[0])
                except Exception as ex:
                    print("_____________________________________________________")
                    driver.close()
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[-1])
                    seen.remove(account)
            except Exception as ex :
                pass
            finally:
                driver.quit()



            
  

    