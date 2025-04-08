
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


def submisson(driver,attempt,submit=1):
        t1 = threading.Thread(target=handle_submission_error,args=(driver,),daemon= True)
        t1.start()
        submit = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,".ui.button.problems_submit_button__6QoNQ"))
        )
        submit.click()
        
        try:
            solved = WebDriverWait(driver,15).until(
            EC.presence_of_element_located((By.CLASS_NAME,"problems_problem_solved_successfully__Zb4yG"))
            )
            time.sleep(2)
            driver.close()
            # Switch back to the previous tab (which is now the last one)
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            # print("Problem not solved")
            
            submit=0
            time.sleep(1)
            if attempt >1:
                driver.close()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[-1])
            return submit
        finally :
            return submit
            

def get_response (driver,question , code_snippet , cir_queue,submit=1,lan=None):
    your_api_key = cir_queue[0]
    attempt =1
    message=""
    try :
        client = OpenAI(
        base_url="https://api.aimlapi.com/v1",
        api_key=your_api_key,  
        )

        if submit==1:
            response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant who knows everything.",
                },
                {
                    "role": "user",
                    "content": f"""response back the answer only , not anything rather than the solution (in {lan}) no need to include any header file also , 
                    just complete the code snippet , write the code like you are directly writing into the editor , no need to add any special character or mention language name "
                    always write the solution in Solution Class  , if selected language supports OOPS concept.
                    follow these strictly.
                    problem statement : {question}
                    code snippet : {code_snippet}"""
                },
            ],
            )
            message = response.choices[0].message.content+"\n"
            error_list=["```",f"java\n",f"cpp\n",f"python\n",f"c\n",f"javascript\n"]  # some times AI mentions code languages in response so we need to fix this
            for items in error_list:
                    message = message.replace(items,"")
            clear_editor(message,driver,lan)
            time.sleep(0.5)
            submit = submisson(driver,submit)
            # print(message)
        
        while submit==0 and attempt <2:
                error_msg = fetch_error(driver)
                attempt+=1
                response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant who knows everything.",
                    },
                    {
                        "role": "user",
                        "content": f"""There was a problem with the previous code , write a new one .
                        response back the answer only , not anything rather than the solution (in {lan}) . no need to include any header file also , 
                        just complete the code snippet , write the code like you are directly writing into the editor , no need to add any special character or mention language name,
                        always write the solution in "Solution Class" if selected language supports OOPS concept.
                        follow these strictly.
                        previous error : {error_msg}
                        problem statement : {question}
                        code snippet : {code_snippet}"""
                    },
                ],
                )
                message = response.choices[0].message.content+"\n"
                error_list=["```",f"java\n",f"cpp\n",f"python\n",f"c\n",f"javascript\n"]  # some times AI mentions code languages in response so we need to fix this
                for items in error_list:
                    message = message.replace(items,"")
                clear_editor(message,driver,lan)
                time.sleep(0.8)
                submit = submisson(driver,attempt,submit)

    except Exception as ex :
        print (f"API key {your_api_key} used , switching to new one")
        cir_queue.append(your_api_key)
        raise api_change_exception("switching to new api")






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

def handle_problem(driver,problem,cir_queue):
    problem.click()
    time.sleep(2)
    window_handles = driver.window_handles 
    driver.switch_to.window(window_handles[-1])
    time.sleep(2)
    selected_lan = select_language(driver)
    question = fetch_content(driver)
    code_snip = fetch_code_snip(driver)
    
    get_response(driver,question,code_snip,cir_queue,lan=selected_lan)




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
        
        
        api_list = [] #**********Enter Your API Keys here****************
        cir_queue = deque(api_list,maxlen=len(api_list))

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        url =  "https://www.geeksforgeeks.org/explore?page=1&sortBy=submissions&ref=home-articlecards" # fixed url 
        driver.get(url)

        uname = ""  # ***************user name and password ***************
        password  = "" # *************your password**************

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
        
        WebDriverWait(driver,15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "infinite-scroll-component"))
        )

        scroll_container = driver.find_element(By.CLASS_NAME, "infinite-scroll-component")


        while True:
            try:
                
                
                WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "explore_problem__XatX9"))
                )

                problems = driver.find_elements(By.CLASS_NAME, "explore_problem__XatX9")
                new_problem_found = False

                for index in range(len(problems)):
                    try:
                            # Re-fetch the problem to avoid stale references
                        problems = driver.find_elements(By.CLASS_NAME, "explore_problem__XatX9")
                        problem = problems[index]

                            # Unique identifier
                        problem_id =  problem.text.strip()
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

                    except Exception as e:
                        # print(f"[ERROR] Could not solve problem at index {index}: {e}")
                        pass
            
            except KeyboardInterrupt as ex :
                print("exiting...")
                exit(0)
            except Exception as e:
               print("______________________________________________________")
               driver.close()
               time.sleep(1)
               driver.switch_to.window(driver.window_handles[-1])
               seen_ids.remove(problem_id)
               time.sleep(2)
               continue
        exit(0)