import os
import time
import random 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. 사용자 정보 로드 ---
PA_USERNAME = os.environ.get('PA_USERNAME')
PA_PASSWORD = os.environ.get('PA_PASSWORD')

if not PA_USERNAME or not PA_PASSWORD:
    print("오류: GitHub Secrets에 PA_USERNAME 또는 PA_PASSWORD가 설정되지 않았습니다.")
    exit(1)

# --- 2. 브라우저 설정 ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

print(">>> 자동 연장 스크립트를 시작합니다.")

try:
    # 봇 탐지 방지를 위한 랜덤 지연 (0~20분)
    delay = random.randint(0, 0)
    print(f"안전한 접속을 위해 {delay // 60}분 {delay % 60}초 대기합니다...")
    time.sleep(delay)

    # 1) 로그인 페이지 접속
    print("1. 로그인 페이지 접속")
    driver.get('https://www.pythonanywhere.com/login/')

    # 2) 로그인 정보 입력 및 제출
    print("2. 로그인 시도")
    user_field = wait.until(EC.visibility_of_element_located((By.ID, 'id_auth-username')))
    pass_field = driver.find_element(By.ID, 'id_auth-password')
    
    user_field.send_keys(PA_USERNAME)
    pass_field.send_keys(PA_PASSWORD)
    
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'id_next')))
    driver.execute_script("arguments[0].click();", login_btn)

    # 3) Web 탭으로 이동 (세션 확인 포함)
    print("3. Web 탭으로 이동")
    time.sleep(5) # 로그인 처리 대기
    webapps_url = f'https://www.pythonanywhere.com/user/{PA_USERNAME}/webapps/'
    driver.get(webapps_url)
    
    # 페이지 제목과 로딩 확인
    wait.until(lambda d: PA_USERNAME in d.current_url and "PythonAnywhere" in d.title)
    print("   - Web 탭 로딩 완료")

    # 4) 연장 버튼 탐색 및 강제 클릭
    print("4. 연장 버튼 탐색 및 클릭")
    time.sleep(3)
    # 바닥까지 스크롤
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 'Run until' 텍스트를 포함한 모든 요소 찾기
    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Run until') or contains(@value, 'Run until')]")
    
    if not buttons:
        raise Exception("연장 버튼을 찾을 수 없습니다.")

    for i, btn in enumerate(buttons):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print(f"   - {i+1}번 후보 클릭 성공")
        except:
            continue

    print(">>> [성공] 모든 연장 프로세스가 완료되었습니다.")

except Exception as e:
    print(f"\n[실패] 오류 발생: {e}")
    driver.save_screenshot("error_screenshot.png")
    exit(1)

finally:
    driver.quit()
    print(">>> 스크립트 종료")
