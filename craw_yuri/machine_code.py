import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Chrome WebDriver 초기화
browser = webdriver.Chrome()

url = "https://www.wanted.co.kr/wdlist/518/1634?country=kr&job_sort=job.recommend_order&years=-1&locations=all"
USERNAME = '*******'
PASSWORD = '********'

# 해당 페이지 열기
browser.get(url)

#로그인 페이지 열기
login_button = browser.find_elements(By.XPATH, '//span[@class="Button_Button__interaction__kkYaa"]')[0]
login_button.click()
time.sleep(5)

#이메일로 로그인하기 페이지 열기
email_login = browser.find_element(By.CLASS_NAME,"css-kfktv3")
email_login.click()
time.sleep(5)

#이메일 입력 필드에 이메일 입력
email_input = browser.find_element(By.NAME, 'email')
email_input.send_keys(USERNAME)

# 비밀번호 입력 필드에 비밀번호 입력
password_input = browser.find_element(By.NAME, 'password')
password_input.send_keys(PASSWORD)

# 로그인 버튼 클릭
login_button = browser.find_element(By.CSS_SELECTOR, 'button[data-testid="Button"]')
login_button.click()

time.sleep(5)  # 로그인이 완료되고 페이지가 로드될 때까지 충분한 시간 대기

def scroll_down(browser):
    # 현재 높이 가져오기
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # 끝까지 스크롤 다운
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 2초 대기
        time.sleep(2)

        # 새로운 높이 가져오기
        new_height = browser.execute_script("return document.body.scrollHeight")

        # 새로운 높이와 이전 높이가 같으면 스크롤 종료
        if new_height == last_height:
            break

        last_height = new_height

    # 스크롤 다운 후의 페이지 소스 가져오기
    html = browser.page_source

    # BeautifulSoup을 사용하여 html 파싱
    soup = BeautifulSoup(html, 'html.parser')

    return soup


# 스크롤 다운 후에 새로운 페이지의 정보를 가져옴
soup = scroll_down(browser)

time.sleep(5)

data = []

# 하위 페이지에 접속하여 직무 관련 텍스트 가져오기
for index, link in enumerate(soup.select('a'), start=1):
    # <a> 태그 안의 href 속성 확인
    href = link.get('href')


    if href and href.startswith('/wd/'):
        detail_page_url = 'https://www.wanted.co.kr/' + href

        browser.get(detail_page_url)

        # 해당 텍스트를 가진 버튼을 클릭
        button = browser.find_element(By.XPATH,
                                      '//button[contains(.//span[@class="Button_Button__label__1Kk0v"], "상세 정보 더 보기")]')
        button.click()

        # 페이지를 스크롤하여 새로운 컨텐츠를 로드합니다.
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 현재 페이지의 html 가져오기
        html = browser.page_source

        # BeautifulSoup을 사용하여 html 파싱
        soup = BeautifulSoup(html, 'html.parser')

        # 해당 클래스를 가진 요소들 찾기
        div_elements = soup.find_all("div", class_="JobDescription_JobDescription__paragraph__Iwfqn")

        # 자격 요건과 우대 사항을 담을 리스트 초기화
        qualification_requirements = []
        preferential_treatment = []

        # 2번째와 3번째 요소만 선택
        for div_element in div_elements[1:3]:
            # h3 태그의 텍스트가 "자격요건"이면 자격 요건으로 간주
            if div_element.find('h3').text == "자격요건":
                # p 태그 아래의 span 태그의 텍스트 추출
                qualification_text = div_element.find('p').find('span').text
                # 각 줄을 분리하여 리스트로 만듦
                qualification_requirements = qualification_text.split('\n')
            # h3 태그의 텍스트가 "우대사항"이면 우대 사항으로 간주
            elif div_element.find('h3').text == "우대사항":
                # p 태그 아래의 span 태그의 텍스트 추출
                preferential_text = div_element.find('p').find('span').text
                # 각 줄을 분리하여 리스트로 만듦
                preferential_treatment = preferential_text.split('\n')

        data.append([qualification_requirements, preferential_treatment])

        # 결과 출력
        print("우대 사항:")
        for treatment in preferential_treatment:
            print(treatment)

        print("\n자격 요건:")
        for requirement in qualification_requirements:
            print(requirement)

# 데이터프레임 생성
df = pd.DataFrame(data, columns=["자격요건", "우대사항"])

# CSV 파일로 저장
df.to_csv("job_requirements.csv", index_label="하위 페이지 번호")
