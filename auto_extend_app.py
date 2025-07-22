import os
import time
import random # 랜덤 지연을 위해 추가
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 사용자 정보 설정 ---
# 중요: 코드에 직접 아이디/비밀번호를 적지 마세요!
# 아래는 운영체제의 '환경 변수'에서 정보를 가져오는 안전한 방식입니다.
PA_USERNAME = os.environ.get('PA_USERNAME')
PA_PASSWORD = os.environ.get('PA_PASSWORD')

# 환경 변수 설정 방법 (터미널에서):
# macOS/Linux: export PA_USERNAME="your_username"
# Windows: set PA_USERNAME="your_username"

if not PA_USERNAME or not PA_PASSWORD:
    print("오류: PA_USERNAME 또는 PA_PASSWORD 환경 변수가 설정되지 않았습니다.")
    exit()

# --- Selenium 웹 드라이버 설정 ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 백그라운드에서 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print(">>> 자동 연장 스크립트를 시작합니다.")

try:
    # --- 랜덤 지연 추가 (0~60분) ---
    delay_seconds = random.randint(0, 3600)
    print(f"스크립트 실행을 {delay_seconds // 60}분 {delay_seconds % 60}초 지연합니다...")
    time.sleep(delay_seconds)

    # 1. 로그인 페이지 접속
    print("1. PythonAnywhere 로그인 페이지에 접속합니다.")
    driver.get('https://www.pythonanywhere.com/login/')
    time.sleep(2) # 페이지 로딩 대기

    # 2. 아이디와 비밀번호 입력
    driver.find_element(By.ID, 'id_auth-username').send_keys(PA_USERNAME)
    driver.find_element(By.ID, 'id_auth-password').send_keys(PA_PASSWORD)
    driver.find_element(By.ID, 'id_loginbutton').click()
    print("2. 로그인 정보를 입력하고 제출했습니다.")
    time.sleep(3)

    # 3. Web 탭으로 이동
    driver.get('https://www.pythonanywhere.com/user/' + PA_USERNAME + '/webapps/')
    print("3. Web 탭 페이지로 이동했습니다.")
    time.sleep(3)

    # 4. 연장 버튼 클릭
    # 버튼의 id나 class가 없으므로, 버튼의 텍스트를 포함하는 input을 찾습니다.
    try:
        print("4. 연장 버튼을 찾습니다...")
        # WebDriverWait를 사용하여 버튼이 클릭 가능할 때까지 최대 20초 대기
        extend_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[contains(@value, 'Run until')]"))
        )
        extend_button.click()
        print(">>> 성공: 웹 앱 기간을 성공적으로 연장했습니다!")
    except Exception as e:
        print("--- 정보: 연장 버튼을 찾을 수 없습니다. 이미 연장되었거나, 만료일이 많이 남았을 수 있습니다.")
        # print(f"발생한 예외: {e}") # 디버깅 시 사용

except Exception as e:
    print(f"스크립트 실행 중 오류가 발생했습니다: {e}")

finally:
    # 5. 드라이버 종료
    driver.quit()
    print(">>> 스크립트를 종료합니다.")