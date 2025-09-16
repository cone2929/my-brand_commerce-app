재활용 체크리스트 (쿠팡/유사 사이트)

1) 드라이버/프로필
- undetected-chromedriver + Selenium
- --user-data-dir 로 프로필 고정(세션/쿠키 유지)
- --lang=ko-KR, --start-maximized, (headless면 --headless=new)

2) 대기/타임아웃
- networkidle 금지, 요소 기반 wait (presence_of_element_located)
- page load timeout 45s, 개별 요소 wait 20~25s

3) 행동/패턴
- 랜덤 지연(human_delay), 점진 스크롤(incremental_scroll)
- 너무 빠른 연속 요청 금지, 키워드 간 짧은 휴식

4) 추출 전략
- 다중 후보 셀렉터(name/price/link/image)
- 결과 없을 때 레이아웃 B 플랜(a.search-product-link)

5) 예외/복구
- 로봇 방지 문구 감지 시 백오프 및 세션 교체
- 키워드 단위 try/except로 배치 진행 지속

6) 저장/로그
- CSV/JSON 동시 저장, UTF-8-SIG로 엑셀 호환
- timestamp 포함 파일명으로 버전 관리

7) 문제 발생시
- 프로필 새로 생성해 테스트
- 헤드풀 ↔ headless(new) 전환 비교
- wait 셀렉터를 실제 렌더 요소로 재점검
