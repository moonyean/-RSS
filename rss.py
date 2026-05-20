import xml.etree.ElementTree as ET
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.korea.kr/rss/policy.xml" # 원하는 RSS 피드 URL로 변경 가능

# 1. 브라우저 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

try:
    print("브라우저를 구동하여 정부 브리핑 RSS에 접근 중입니다... (시간이 수 초 소요될 수 있습니다)")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get(url)
    time.sleep(0.5)  # 로딩 대기
    
    # 브라우저가 화면에 뿌린 전체 텍스트/HTML 가져오기
    raw_source = driver.page_source
    driver.quit()

    # 2. [핵심] 정규식을 이용해 순수한 XML 데이터만 추출하기
    xml_match = re.search(r'(<\?xml.*?</rss>)', raw_source, re.DOTALL | re.IGNORECASE)
    
    if xml_match:
        xml_data = xml_match.group(1).strip()
    else:
        # 혹시 <?xml 선언문이 생략된 경우 <rss> 태그 기준으로 한 번 더 찾음
        xml_match_alt = re.search(r'(<rss.*?</rss>)', raw_source, re.DOTALL | re.IGNORECASE)
        if xml_match_alt:
            xml_data = xml_match_alt.group(1).strip()
        else:
            # 정규식으로도 못 찾으면 앞뒤 공백만 제거하고 시도
            xml_data = raw_source.strip()

    # 3. XML 파싱
    root = ET.fromstring(xml_data)

    # 4. 데이터 추출 및 출력 + TXT 파일 저장 추가
    items = root.findall('.//item')
    
    print(f"\n✅ 성공적으로 {len(items)}개의 정책 뉴스를 가져왔습니다!\n")
    print("-" * 60)
    
    # utf-8 인코딩으로 txt 파일을 열어 기록합니다.
    with open("policy_news.txt", "w", encoding="utf-8") as f:
        f.write(f"✅ 성공적으로 {len(items)}개의 정책 뉴스를 가져왔습니다!\n")
        f.write("-" * 60 + "\n")
        
        for item in items:
            title = item.find('title').text if item.find('title') is not None else "제목 없음"
            link = item.find('link').text if item.find('link') is not None else "링크 없음"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "날짜 없음"
            description = item.find('description').text if item.find('description') is not None else ""
            
            # 화면 출력
            print(f"📌 제목: {title}")
            print(f"📅 일시: {pub_date}")
            print(f"🔗 링크: {link}")
            
            # 파일 기록
            f.write(f"📌 제목: {title}\n")
            f.write(f"📅 일시: {pub_date}\n")
            f.write(f"🔗 링크: {link}\n")
            
            if description:
                # 설명글에 들어있는 HTML 태그나 불필요한 공백 제거
                clean_desc = re.sub(r'<[^>]*>', '', description).strip()
                print(f"📝 내용: {clean_desc}...")
                f.write(f"📝 내용: {clean_desc}...\n")
                
            print("-" * 60)
            f.write("-" * 60 + "\n")
            
    print("\n💾 'policy_news.txt' 파일로 저장이 완료되었습니다.")

except Exception as e:
    print(f"\n❌ 에러가 발생했습니다. 원인: {e}")
    if 'driver' in locals():
        try:
            driver.quit()
        except:
            pass
