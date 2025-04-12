
# Note : don't use it if u really want to learn  


# *************  AI can make mistakes **************

# follow comments marked with ************

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
import winsound
import requests


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



class problem_not_solved_exception(Exception):
    pass

def handle_submission_error(driver):
    while True:
        try:
            ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']"))
            )
            driver.execute_script("arguments[0].click();", ok_button)  
        except Exception as e:
            pass



def filter_problems(status=None,difficulty=None):
    difficult_dict = {0:"Basic",1:"Easy",2:"Medium",3:"Hard"}
    status_dict ={0:"Solved",1:"Unsolved",2:"Attempted"}
    try:
        if difficulty is not None:
            for ele in difficulty:
                filters = driver.find_element(By.XPATH, "//div[@class= 'explore_sectionHeaderLabel__k0pX8']//h3[text()='Difficulty']")
                script = """arguments[0].scrollIntoView(true);
                        arguments[0].click();"""
                driver.execute_script(script, filters)

                label = driver.find_element(By.XPATH, f'//label[contains(., "{difficult_dict.get(ele)}")]')
                driver.execute_script("arguments[0].scrollIntoView(true);", label)
                label.click()
                time.sleep(0.7)
                driver.execute_script(script, filters)

        if status is not None :
            for ele in status:
                filters = driver.find_element(By.XPATH, "//div[@class= 'explore_sectionHeaderLabel__k0pX8']//h3[text()='Status']")
                script = """arguments[0].scrollIntoView(true);
                        arguments[0].click();"""
                driver.execute_script(script, filters)

                label = driver.find_element(By.XPATH, f'//label[contains(., "{status_dict.get(ele)}")]')
                driver.execute_script("arguments[0].scrollIntoView(true);", label)
                label.click()
                time.sleep(0.7)
                driver.execute_script(script, filters)
  
    except Exception :
        pass 


class api_change_exception(Exception):
    pass

# method to detect if error during testing 
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


def submisson(driver):
        t1 = threading.Thread(target=handle_submission_error,args=(driver,),daemon= True)
        t1.start()
        submit = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,".ui.button.problems_submit_button__6QoNQ"))
        )
        driver.execute_script("""arguments[0].scrollIntoView(true);
                                 arguments[0].click()""",submit )
        
        try:
            solved = WebDriverWait(driver,20).until(
            EC.presence_of_element_located((By.CLASS_NAME,"problems_problem_solved_successfully__Zb4yG"))
            )
            return True
        except Exception:
            print("Not submitted")
            return False
        



def get_response(driver, question, code_snippet, cir_queue, lan=None):
    submit = None
    attempt = 0
    message = ""
    
    while attempt < 2:
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
                break  
                
        except Exception as ex:
            print(f"API key {your_api_key} failed , switching to new one ")
            cir_queue.append(your_api_key)  # Rotate to next API key
            time.sleep(1)  # Add delay before retry
            driver.close()
            raise api_change_exception()
    
            
        attempt += 1

    if not submit:
        raise problem_not_solved_exception()



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
            }}, {safe_code} +"\\n");

            editor.moveCursorTo(logicStart, 0);
        }}
    """
    driver.execute_script(js_script)



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
        question+=str.text
    question.replace(' ','')
    return question

def handle_problem(driver, problem, cir_queue):
    problem.click()
    time.sleep(2)
    window_handles = driver.window_handles 
    driver.switch_to.window(window_handles[-1])
    time.sleep(2)
    selected_lan = select_language(driver)
    question = fetch_content(driver)
    code_snip = fetch_code_snip(driver)
    
    try:
        get_response(driver, question, code_snip, cir_queue, lan=selected_lan)
    except problem_not_solved_exception:
        print("Problem could not be solved after multiple attempts")
        driver.close()
        driver.switch_to.window(window_handles[0])  # Switch back to main window
        time.sleep(2)
        return False
    return True




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
        msg = "Successful login"
    except Exception:
       msg=  "Internet issue"
    #    exit(1)
    return msg




if __name__ == "__main__":
    
    url =  "https://www.geeksforgeeks.org/explore?page=1&sortBy=submissions&ref=home-articlecards"
    
    if not is_online(url):
        print("you are offline , exiting....")
        make_beep()
        exit(1)

    api_list = [""] #**********Enter Your API Keys here****************
    cir_queue = deque(api_list,maxlen=len(api_list))

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)

    uname = "example@gmail
    com"  # ***************user name and password ***************
    password  = "password" # *************your password**************

    log_in_first(driver,uname,password) 

                                                    # **********difficult_dict = {0:"Basic",1:"Easy",2:"Medium",3:"Hard"}*********
                                                    # **********status_dict ={0:"Solved",1:"Unsolved",2:"Attempted"}*************  
    filter_problems(status=[1,2],difficulty=[2,3])   #********* choose difficulty and problem status ************
    time.sleep(1)

    seen_ids = set()
    problem_id=""
    try:
        cookies = WebDriverWait(driver,15).until(
        EC.presence_of_element_located((By.CLASS_NAME,"cookieConsent_gfg_cookie__button__y3NOr"))
        )
        cookies.click()
    except Exception:
        pass
    
    # Wait for the initial load of problems
    try:
        WebDriverWait(driver,15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "infinite-scroll-component"))
        )
    except Exception as e:
        print(f"Error loading initial problems: {e}")
        driver.quit()
        exit(1)

    scroll_container = driver.find_element(By.CLASS_NAME, "infinite-scroll-component")

    while True:
        try:
            # Properly wait for problems with a proper timeout and error handling
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "explore_problem__XatX9"))
                )
            except Exception as e:
                print(f"Error waiting for problems: {e}")
                # Try refreshing the page
                driver.refresh()
                time.sleep(5)
                continue

            problems = driver.find_elements(By.CLASS_NAME, "explore_problem__XatX9")
            new_problem_found = False

            for index in range(len(problems)):
                try:
                    # Re-fetch the problem to avoid stale references
                    problems = driver.find_elements(By.CLASS_NAME, "explore_problem__XatX9")
                    problem = problems[index]

                    # Unique identifier
                    problem_id = problem.text.strip()
                    if problem_id in seen_ids:
                        continue
                    seen_ids.add(problem_id)

                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", problem)
                    time.sleep(0.5)

                    # Find the correct button inside the current problem card
                    button = problem.find_element(By.CSS_SELECTOR, "button.explore_problemSolveBtn__ZF8_I")

                    if "Solved" in button.text.strip():
                        # print(f"[SKIP] Problem {problem_id} already solved.")
                        continue

                    handle_problem(driver, problem, cir_queue)
                    new_problem_found = True
                    time.sleep(0.5)

                except api_change_exception:
                    print("API key rotation occurred, returning to main window")
                    
                    seen_ids.remove(problem_id)
                   
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)
                    break
                    
                except Exception as e:
                    # print(f"[ERROR] Could not solve problem at index {index}: {e}")
                    # Handle any stray windows that might be open
                    if len(driver.window_handles) > 1:
                        for handle in driver.window_handles[1:]:
                            driver.switch_to.window(handle)
                            driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)
                    continue
            
            # Scroll down to load more problems if no new ones were found
            if not new_problem_found:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                time.sleep(2)

        except KeyboardInterrupt:
            print("Exiting gracefully...")
            driver.quit()
            exit(0)
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            # Try to recover
            try:
                if len(driver.window_handles) > 1:
                    for handle in driver.window_handles[1:]:
                        driver.switch_to.window(handle)
                        driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.refresh()
                time.sleep(5)
            except:
                # If recovery fails, restart the browser
                try:
                    driver.quit()
                except:
                    pass
                driver = webdriver.Chrome()
                driver.maximize_window()
                driver.get(url)
                log_in_first(driver, uname, password)
                filter_problems(status=[1,2], difficulty=[2,3])
                time.sleep(5)
