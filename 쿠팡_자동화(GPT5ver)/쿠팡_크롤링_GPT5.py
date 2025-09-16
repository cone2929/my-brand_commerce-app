import os
import csv
import sys
import time
import json
import random
import argparse
from pathlib import Path

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def log(msg: str):
	ts = time.strftime("%H:%M:%S")
	print(f"[{ts}] {msg}")


def build_driver(profile_dir: Path, headless: bool = False):
	options = uc.ChromeOptions()
	options.add_argument("--lang=ko-KR")
	options.add_argument("--disable-features=PasswordManagerEnabled")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument("--start-maximized")
	options.add_argument(f"--user-data-dir={str(profile_dir)}")
	# 안정성 옵션
	options.add_argument("--no-first-run")
	options.add_argument("--no-default-browser-check")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--no-sandbox")

	if headless:
		# 헤드리스라도 새 크롬(헤드리스=뉴) 모드가 탐지에 더 강함
		options.add_argument("--headless=new")

	driver = uc.Chrome(options=options, use_subprocess=True)
	driver.set_page_load_timeout(45)
	driver.implicitly_wait(0)
	return driver


def wait_css(driver, css: str, timeout: int = 20):
	return WebDriverWait(driver, timeout).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, css))
	)


def wait_all_css(driver, css: str, timeout: int = 20):
	return WebDriverWait(driver, timeout).until(
		EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
	)


def human_delay(a: float = 0.4, b: float = 1.3):
	time.sleep(random.uniform(a, b))


def navigate_and_search(driver, keyword: str):
	log("쿠팡 접속 중…")
	driver.get("https://www.coupang.com/")
	human_delay(1.0, 2.2)

	# 쿠팡은 검색창 id가 자주 유지됨
	selectors = [
		"#headerSearchKeyword",
		'input[name="q"]',
		'input[placeholder*="검색"]',
	]
	search_box = None
	for s in selectors:
		try:
			search_box = wait_css(driver, s, timeout=20)
			if search_box:
				log(f"검색창 탐지: {s}")
				break
		except TimeoutException:
			continue

	if not search_box:
		raise RuntimeError("검색창을 찾지 못했습니다. 쿠팡 레이아웃 변경 가능성.")

	search_box.clear()
	human_delay()
	search_box.send_keys(keyword)
	human_delay()
	search_box.send_keys(Keys.ENTER)

	# URL 변화 대기: /search?q= 또는 /np/search
	try:
		WebDriverWait(driver, 15).until(
			EC.url_matches(r"/search\?|/np/search")
		)
	except TimeoutException:
		pass  # 일부 환경에서 URL 매칭이 늦을 수 있어 continue

	# 결과 페이지 감지(강화): JS로 다중 셀렉터 카운트 + 소프트 스크롤 재시도
	start = time.time()
	timeout = 30
	found = False
	while time.time() - start < timeout:
		try:
			cnt = driver.execute_script(
				"return document.querySelectorAll(\"li.search-product, a.search-product-link[href*='/vp/products'], ul.search-product-list li, ul#productList li, .search-product-wrap li, [data-product-id]\").length;"
			)
			if cnt and int(cnt) > 0:
				log(f"결과 감지: {cnt}개 요소")
				found = True
				break
		except Exception:
			pass

		# 한 번씩 작은 스크롤로 레이지로드 트리거
		driver.execute_script("window.scrollBy(0, 600);")
		human_delay(0.4, 0.9)

	if found:
		return True

	# 혹시 지역/성인 인증, 로봇차단 등 인터럽트 처리
	page_src = driver.page_source
	if "자동입력 방지" in page_src or "로봇이 아닙니다" in page_src:
		raise RuntimeError("로봇차단 페이지가 표시되었습니다.")

	# URL/제목이 검색 맥락이면 성공으로 간주(추출 단계에서 재판단)
	cur_url = driver.current_url
	title = driver.title
	if "search" in cur_url or (keyword in title):
		log("검색 맥락 감지(URL/제목). 추출 단계로 진행")
		return True

	raise RuntimeError("검색결과 로드에 실패했습니다.")


def incremental_scroll(driver, target_count: int = 60, max_scrolls: int = 20):
	last_h = 0
	same_count = 0
	for i in range(max_scrolls):
		driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
		human_delay(0.8, 1.6)
		new_h = driver.execute_script("return document.body.scrollHeight")
		if new_h == last_h:
			same_count += 1
		else:
			same_count = 0
		last_h = new_h

		cards = driver.find_elements(By.CSS_SELECTOR, "li.search-product, a.search-product-link[href*='/vp/products']")
		if len(cards) >= target_count:
			break
		if same_count >= 2:
			break


def extract_products(driver, limit: int = 50):
	items = []
	# 다양한 레이아웃 대응: 우선순위 순으로 병합
	cards = driver.find_elements(By.CSS_SELECTOR, "li.search-product")
	if not cards:
		cards = driver.find_elements(By.CSS_SELECTOR, "ul#productList li") + \
				driver.find_elements(By.CSS_SELECTOR, "ul.search-product-list li")
	if not cards:
		cards = driver.find_elements(By.CSS_SELECTOR, "a.search-product-link[href*='/vp/products']")

	for el in cards:
		try:
			name = None
			price = None
			link = None
			image = None

			try:
				name_el = el.find_element(By.CSS_SELECTOR, ".name, .title, .prod-name")
				name = name_el.text.strip()
			except NoSuchElementException:
				pass

			try:
				price_el = el.find_element(By.CSS_SELECTOR, ".price-value, strong.price-value, .price, .total-price strong, .prod-price, .price-info, em.sale-price")
				price = price_el.text.strip()
			except NoSuchElementException:
				pass

			try:
				a_el = el.find_element(By.CSS_SELECTOR, "a[href*='/vp/products'], a[href*='/products/']")
				link = a_el.get_attribute("href")
			except NoSuchElementException:
				try:
					link = el.get_attribute("href")
				except Exception:
					pass

			try:
				img_el = el.find_element(By.CSS_SELECTOR, "img")
				image = img_el.get_attribute("src")
			except NoSuchElementException:
				pass

			if name or link:
				items.append({
					"name": name,
					"price": price,
					"link": link,
					"image": image,
				})
		except Exception:
			continue

		if len(items) >= limit:
			break

	return items


def save_results(rows, out_prefix: str, out_dir: Path):
	out_dir.mkdir(parents=True, exist_ok=True)
	csv_path = out_dir / f"{out_prefix}.csv"
	json_path = out_dir / f"{out_prefix}.json"

	with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
		w = csv.DictWriter(f, fieldnames=["name", "price", "link", "image"])
		w.writeheader()
		for r in rows:
			w.writerow(r)

	with open(json_path, "w", encoding="utf-8") as f:
		json.dump(rows, f, ensure_ascii=False, indent=2)

	return str(csv_path), str(json_path)


def save_results_multi(rows, out_prefix: str, out_dir: Path):
	out_dir.mkdir(parents=True, exist_ok=True)
	csv_path = out_dir / f"{out_prefix}.csv"
	json_path = out_dir / f"{out_prefix}.json"

	base_order = ["keyword", "name", "price", "link", "image"]
	all_keys = set().union(*[r.keys() for r in rows]) if rows else set(base_order)
	fieldnames = [k for k in base_order if k in all_keys] + [k for k in sorted(all_keys) if k not in base_order]

	with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
		w = csv.DictWriter(f, fieldnames=fieldnames)
		w.writeheader()
		for r in rows:
			w.writerow(r)

	with open(json_path, "w", encoding="utf-8") as f:
		json.dump(rows, f, ensure_ascii=False, indent=2)

	return str(csv_path), str(json_path)


def search_one_keyword(driver, keyword: str, limit: int):
	log(f"[{keyword}] 검색 시작")
	ok = navigate_and_search(driver, keyword)
	if not ok:
		raise RuntimeError(f"[{keyword}] 검색 진입 실패")
	incremental_scroll(driver, target_count=limit)
	rows = extract_products(driver, limit=limit)
	for r in rows:
		r["keyword"] = keyword
	log(f"[{keyword}] 수집 {len(rows)}건")
	return rows


def main():
	parser = argparse.ArgumentParser(description="쿠팡 검색 크롤러 (undetected-chromedriver)")
	parser.add_argument("keyword", nargs="?", help="검색 키워드 (단일)")
	parser.add_argument("-n", "--limit", type=int, default=50, help="가져올 상품 수")
	parser.add_argument("--headless", action="store_true", help="헤드리스 모드 사용")
	parser.add_argument("--profile", default=str(Path("chrome-profile-coupang").absolute()), help="크롬 프로필 디렉터리")
	parser.add_argument("--out", default="results", help="결과 저장 폴더")
	parser.add_argument("--keywords", help="쉼표(,)로 구분한 다중 키워드 목록")
	parser.add_argument("--kw-file", help="줄바꿈으로 구분된 키워드 파일 경로")
	parser.add_argument("--batch", action="store_true", help="키워드 미지정 시 기본 5개 샘플로 배치 실행")
	args = parser.parse_args()

	profile_dir = Path(args.profile)
	out_dir = Path(args.out)

	# 키워드 소스 결정
	kw_list = []
	if args.keywords:
		kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
	elif args.kw_file:
		with open(args.kw_file, "r", encoding="utf-8") as f:
			kw_list = [line.strip() for line in f if line.strip()]
	elif args.keyword:
		kw_list = [args.keyword]
	elif args.batch:
		kw_list = ["에어팟", "허리보조쿠션", "커피머신", "게이밍 마우스", "캠핑 의자"]
	else:
		# 입력이 전혀 없으면 안내
		log("키워드를 지정하지 않아 기본 샘플 5개로 실행합니다. --batch 사용 가능")
		kw_list = ["에어팟", "허리보조쿠션", "커피머신", "게이밍 마우스", "캠핑 의자"]

	driver = None
	try:
		driver = build_driver(profile_dir, headless=args.headless)

		all_rows = []
		for kw in kw_list:
			try:
				rows = search_one_keyword(driver, kw, limit=args.limit)
				all_rows.extend(rows)
				human_delay(1.0, 2.0)
			except Exception as e:
				log(f"[{kw}] 실패: {e}")
				continue

		ts = time.strftime("%Y%m%d_%H%M%S")
		if len(kw_list) == 1:
			prefix = f"coupang_{kw_list[0]}_{ts}"
			csv_path, json_path = save_results(all_rows, prefix, out_dir)
		else:
			prefix = f"coupang_batch_{ts}"
			csv_path, json_path = save_results_multi(all_rows, prefix, out_dir)

		log(f"저장 완료: {csv_path}, {json_path}")
	finally:
		if driver:
			try:
				driver.quit()
			except Exception:
				pass


if __name__ == "__main__":
	# PowerShell에서: python .\\my-brand_commerce-app\\쿠팡_크롤링_GPT5.py "키워드"
	main()

