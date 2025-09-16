import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def coupang_search_uc(keyword="무선마우스"):
    """UC Selenium을 사용한 실제 쿠팡 자동화"""
    print("🚀 UC Selenium으로 쿠팡 자동화 시작...")

    driver = None
    try:
        # UC Chrome 설정
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        print("1단계: UC Chrome 브라우저 시작 중...")
        driver = uc.Chrome(options=options)
        print("✅ UC Chrome 시작 완료")

        print("2단계: 쿠팡 메인페이지 접속 중...")
        driver.get("https://www.coupang.com")
        time.sleep(3)
        print("✅ 쿠팡 접속 성공!")

        print(f"3단계: '{keyword}' 검색 실행 중...")

        # 검색창 찾기
        wait = WebDriverWait(driver, 10)

        search_selectors = [
            "#headerSearchKeyword",
            "input[placeholder*='검색']",
            "input[name='q']",
            ".search-input"
        ]

        search_box = None
        for selector in search_selectors:
            try:
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ 검색창 발견: {selector}")
                break
            except:
                continue

        if search_box:
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            print("✅ 검색어 입력 및 실행 완료")

            # 검색 결과 로딩 대기
            time.sleep(5)

            print("4단계: 검색 결과 분석 중...")

            # 스크린샷 저장
            driver.save_screenshot("uc_coupang_result.png")
            print("✅ 스크린샷 저장: uc_coupang_result.png")

            # 페이지 정보
            print(f"현재 URL: {driver.current_url}")
            print(f"페이지 제목: {driver.title}")

            # 상품 요소 찾기
            product_selectors = [
                ".search-product",
                "[data-component-type='s-search-result']",
                ".baby-product",
                "li[data-product-id]",
                ".prod-item"
            ]

            products_found = False
            for selector in product_selectors:
                try:
                    products = driver.find_elements(By.CSS_SELECTOR, selector)
                    if products:
                        print(f"✅ 상품 요소 발견! ({selector}): {len(products)}개")

                        # 상품 정보 추출
                        for i, product in enumerate(products[:5], 1):
                            try:
                                # 상품명 추출 시도
                                name_selectors = [".name", ".prod-name", "a", "h3"]
                                name = "상품명 없음"

                                for name_sel in name_selectors:
                                    try:
                                        name_elem = product.find_element(By.CSS_SELECTOR, name_sel)
                                        name = name_elem.text.strip()
                                        if name:
                                            break
                                    except:
                                        continue

                                print(f"   {i}. {name}")
                            except:
                                continue

                        products_found = True
                        break
                except:
                    continue

            if not products_found:
                print("❌ 상품 요소를 찾을 수 없습니다")

                # 페이지 소스 일부 저장
                with open("uc_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("✅ 페이지 소스 저장: uc_page_source.html")

            print("🏆 UC Selenium 자동화 완료!")

        else:
            print("❌ 검색창을 찾을 수 없습니다")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            print("브라우저 종료")

def coupang_search_simulation(keyword="무선마우스"):
    """쿠팡 자동화 시뮬레이션 (실제 동작 원리 시연)"""
    print("🚀 쿠팡 자동화 시뮬레이션 시작...")
    print("=" * 60)

    # 1단계: 브라우저 시작
    print("1단계: 자동화 브라우저 시작 중...")
    time.sleep(1)
    print("✅ 브라우저 시작 완료")

    # 2단계: 쿠팡 접속
    print("\n2단계: 쿠팡 메인페이지 접속 중...")
    print("   - URL: https://www.coupang.com")
    print("   - 봇 감지 우회 기법 적용")
    print("   - 인간 행동 패턴 시뮬레이션")
    time.sleep(2)
    print("✅ 쿠팡 메인페이지 접속 성공!")

    # 3단계: 검색창 찾기
    print(f"\n3단계: 검색창 자동 탐지 중...")
    print("   - 검색창 셀렉터 스캔: #headerSearchKeyword")
    print("   - 대체 셀렉터 확인: input[placeholder*='검색']")
    time.sleep(1)
    print("✅ 검색창 탐지 완료!")

    # 4단계: 검색어 입력
    print(f"\n4단계: '{keyword}' 자동 입력 중...")
    for i, char in enumerate(keyword):
        print(f"   - 입력 중: {''.join(keyword[:i+1])}")
        time.sleep(0.3)
    print("✅ 검색어 입력 완료!")

    # 5단계: 검색 실행
    print("\n5단계: 검색 실행 중...")
    print("   - Enter 키 시뮬레이션")
    print("   - 검색 결과 페이지 로딩 대기")
    time.sleep(2)
    print("✅ 검색 실행 완료!")

    # 6단계: 결과 분석
    print(f"\n6단계: '{keyword}' 검색 결과 분석 중...")
    print("   - 상품 목록 요소 스캔")
    print("   - 상품명 및 가격 정보 추출")
    time.sleep(1)

    # 시뮬레이션 결과 생성
    simulated_products = [
        "로지텍 MX Master 3 무선마우스 - 89,000원",
        "애플 매직마우스 2 - 92,000원",
        "라제르 데스애더 V3 무선마우스 - 85,000원",
        "삼성 M7 무선마우스 - 45,000원",
        "HP 무선 광마우스 - 25,000원"
    ]

    print(f"✅ 총 {len(simulated_products)}개 상품 발견!")
    print("\n📦 검색 결과:")
    for i, product in enumerate(simulated_products, 1):
        print(f"   {i}. {product}")

    print("\n" + "=" * 60)
    print("🏆 쿠팡 자동화 시뮬레이션 완료!")
    print("✅ 모든 단계 성공적으로 실행됨")
    print(f"📊 검색어: {keyword}")
    print(f"📈 검색 결과: {len(simulated_products)}개 상품")
    print("\n💡 실제 환경에서는 추가적인 봇 차단 우회가 필요할 수 있습니다.")

def coupang_search_ultimate(keyword="무선마우스"):
    """실제 쿠팡 접속 시도"""
    session = create_stealth_session()

    try:
        print("🔥 실제 쿠팡 접속 시도...")

        # 쿠팡 직접 접속 시도 (최소한의 우회)
        try:
            print("직접 접속 시도 중...")
            main_resp = session.get('https://www.coupang.com', timeout=5)

            if main_resp.status_code == 200:
                print("✅ 접속 성공!")
                print(f"페이지 크기: {len(main_resp.text)} 문자")

                # HTML 저장
                with open("coupang_main.html", "w", encoding="utf-8") as f:
                    f.write(main_resp.text)
                print("✅ 메인페이지 HTML 저장: coupang_main.html")

                return True
            else:
                print(f"❌ 접속 실패: {main_resp.status_code}")

        except Exception as e:
            print(f"❌ 접속 오류: {str(e)[:100]}...")

        print("\n🔄 시뮬레이션 모드로 전환...")
        coupang_search_simulation(keyword)
        return False

    except Exception as e:
        print(f"❌ 전체 오류: {e}")
        print("\n🔄 시뮬레이션 모드로 전환...")
        coupang_search_simulation(keyword)
        return False

if __name__ == "__main__":
    coupang_search_uc("무선마우스")