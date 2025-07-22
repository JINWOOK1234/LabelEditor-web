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
    exit()

# --- Selenium 웹 드라이버 설정 ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

print(">>> 자동 연장 스크립트를 시작합니다.")

try:
    # --- 랜덤 지연 추가 (0~30분) ---
    delay_seconds = random.randint(0, 1800)
    print(f"스크립트 실행을 {delay_seconds // 60}분 {delay_seconds % 60}초 지연합니다...")
    time.sleep(delay_seconds)

    # 1. 로그인 페이지 접속
    print("1. PythonAnywhere 로그인 페이지에 접속합니다.")
    driver.get('https://www.pythonanywhere.com/login/')
    print(f"   - 현재 페이지 제목: {driver.title}")

    # 쿠키 동의 버튼이 있으면 클릭
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "id_cookieconsent_agree_button")))
        cookie_button.click()
        print("   - 쿠키 동의 버튼을 클릭했습니다.")
        time.sleep(1)
    except Exception:
        print("   - 쿠키 동의 버튼이 없습니다. 계속 진행합니다.")

    # 2. 아이디와 비밀번호 입력
    # [수정] JavaScript를 사용하여 값을 직접 설정하는 방식으로 안정성 강화
    username_field = wait.until(EC.visibility_of_element_located((By.ID, 'id_auth-username')))
    password_field = wait.until(EC.visibility_of_element_located((By.ID, 'id_auth-password')))
    login_button = wait.until(EC.element_to_be_clickable((By.ID, 'id_loginbutton')))

    driver.execute_script("arguments[0].value = arguments[1];", username_field, PA_USERNAME)
    driver.execute_script("arguments[0].value = arguments[1];", password_field, PA_PASSWORD)
    time.sleep(1) # 값 입력 후 잠시 대기
    driver.execute_script("arguments[0].click();", login_button)
    print("2. 로그인 정보를 입력하고 제출했습니다.")
    
    # 3. Web 탭으로 이동
    webapps_url = f'https://www.pythonanywhere.com/user/{PA_USERNAME}/webapps/'
    wait.until(EC.url_contains('dashboard'))
    print("3. Web 탭 페이지로 이동합니다.")
    driver.get(webapps_url)

    # 4. 연장 버튼 클릭
    try:
        print("4. 연장 버튼을 찾습니다...")
        extend_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[contains(@value, 'Run until')]"))
        )
        extend_button.click()
        print(">>> 성공: 웹 앱 기간을 성공적으로 연장했습니다!")
    except Exception:
        print("--- 정보: 연장 버튼을 찾을 수 없습니다. 이미 연장되었거나, 만료일이 많이 남았을 수 있습니다.")

except Exception as e:
    print(f"스크립트 실행 중 오류가 발생했습니다: {e}")

finally:
    # 5. 드라이버 종료
    driver.quit()
    print(">>> 스크립트를 종료합니다.")
