import os
import time
import random 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 사용자 정보 설정 ---
PA_USERNAME = os.environ.get('PA_USERNAME')
PA_PASSWORD = os.environ.get('PA_PASSWORD')

if not PA_USERNAME or not PA_PASSWORD:
    print("오류: PA_USERNAME 또는 PA_PASSWORD 환경 변수가 설정되지 않았습니다.")
    exit(1)

# --- Selenium 웹 드라이버 설정 ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30) # 대기 시간을 30초로 늘림

# --- 랜덤 지연 부분 수정 ---
# 테스트할 때는 아래 3줄을 주석 처리(#) 하거나, 0으로 만드세요.
# delay_seconds = random.randint(0, 1800)
# print(f"스크립트 실행을 {delay_seconds // 60}분 {delay_seconds % 60}초 지연합니다...")
# time.sleep(delay_seconds)

print(">>> 자동 연장 스크립트를 시작합니다.")

try:
    # 1. 로그인 페이지 접속
    print("1. PythonAnywhere 로그인 페이지에 접속합니다.")
    driver.get('https://www.pythonanywhere.com/login/')
    
    # 쿠키 동의 버튼 (있는 경우에만)
    try:
        cookie_button = driver.find_element(By.ID, "id_cookieconsent_agree_button")
        cookie_button.click()
    except:
        pass

    # 2. 로그인 수행
    print("2. 로그인을 시도합니다.")
    # 입력 필드가 나타날 때까지 최대 30초 대기
    try:
        username_field = wait.until(EC.visibility_of_element_located((By.NAME, 'auth-username')))
        password_field = driver.find_element(By.NAME, 'auth-password')
    except:
        # NAME으로 못 찾으면 ID로 재시도
        username_field = wait.until(EC.visibility_of_element_located((By.ID, 'id_auth-username')))
        password_field = driver.find_element(By.ID, 'id_auth-password')

    username_field.send_keys(PA_USERNAME)
    password_field.send_keys(PA_PASSWORD)
    
    # [핵심] 로그인 버튼을 찾는 경로를 여러 개 준비 (하나라도 걸리게)
    login_button_selectors = [
        "button#id_next",
        "input#id_next",
        "//button[contains(text(), 'Log in')]",
        "//input[@type='submit']",
        ".btn-primary"
    ]
    
    login_button = None
    for selector in login_button_selectors:
        try:
            # XPATH와 CSS Selector를 구분해서 시도
            method = By.XPATH if selector.startswith("/") else By.CSS_SELECTOR
            btn = driver.find_element(method, selector)
            if btn.is_displayed():
                login_button = btn
                break
        except:
            continue

    if login_button:
        driver.execute_script("arguments[0].click();", login_button)
        print("   - 로그인 버튼을 클릭했습니다.")
    else:
        # 버튼을 끝내 못 찾으면 현재 화면 저장 후 에러 발생
        driver.save_screenshot("error_screenshot.png")
        raise Exception("Login button (id_next) not found on the page.")
        
    print("   - 로그인 성공!")

    # 3. Web 탭으로 이동 (안전성 강화 버전)
    print("3. Web 탭 페이지로 이동을 시도합니다.")
    
    # [추가] 로그인이 완전히 처리되어 대시보드 UI가 보일 때까지 대기
    try:
        # 로그아웃 링크나 사용자 이름이 보이면 로그인이 완료된 것
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Log out")))
        print("   - 로그인 세션 확인 완료.")
    except:
        print("   - 세션 확인 지연 중... 일단 이동을 시도합니다.")

    webapps_url = f'https://www.pythonanywhere.com/user/{PA_USERNAME}/webapps/'
    
    # URL 이동 후 페이지가 완전히 로딩될 때까지 최대 3번 재시도
    for attempt in range(3):
        try:
            driver.get(webapps_url)
            # Web 탭의 고유한 요소(Web apps 리스트 섹션)가 나타나는지 확인
            wait.until(EC.presence_of_element_located((By.ID, 'id_web_app_setup_section')))
            print(f"   - {attempt+1}차 시도: Web 탭 로딩 성공!")
            break
        except Exception as e:
            print(f"   - {attempt+1}차 시도 실패, 재시도 중...")
            time.sleep(3)
            if attempt == 2:
                driver.save_screenshot("web_tab_move_error.png")
                raise Exception("Web 탭으로 이동하지 못했습니다.")

    # 4. 연장 버튼 클릭 (이전의 '싹 다 눌러' 버전 유지)
    # ... (이후 코드는 동일)

    # 4. 연장 버튼 클릭 (가장 강력한 버전)
    print("4. 연장 버튼(Run until...)을 찾는 중...")
    
    # 페이지가 완전히 안정화될 때까지 잠시 대기
    time.sleep(5) 

    try:
        # 1. 버튼이 나타날 때까지 기다림 (By.NAME이 더 정확할 수 있음)
        extend_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@value, 'Run until')]")
        ))
        
        # 2. 스크롤을 아주 아래까지 충분히 내림 (전체 페이지 높이만큼)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 3. 버튼이 화면에 보이지 않아도 '강제로' 클릭 명령 전달 (JavaScript 방식)
        # 이 방식은 물리적 클릭이 아니라 브라우저 엔진에 직접 "이 버튼 눌러!"라고 명령하는 거라 가장 확실합니다.
        driver.execute_script("arguments[0].click();", extend_button)
        
        print(">>> 성공: 웹 앱 기간을 성공적으로 연장했습니다!")
        
        # 성공 후 화면 확인을 위해 3초 대기 후 스크린샷
        time.sleep(3)
        driver.save_screenshot("after_click_success.png")

    except Exception as e:
        driver.save_screenshot("last_error_screenshot.png")
        print(f"!!! 실패: 버튼을 찾았으나 클릭에 실패했습니다. 오류: {e}")
        raise e
        
except Exception as e:
    print(f"\n[오류 발생] 스크립트가 중단되었습니다: {e}")
    driver.save_screenshot("error_screenshot.png")
    exit(1) # GitHub Actions에 실패(빨간색)를 보고합니다.

finally:
    driver.quit()
    print(">>> 스크립트를 종료합니다.")
