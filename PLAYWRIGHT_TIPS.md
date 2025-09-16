쿠팡 크롤링 Playwright 개선 팁

- channel=chrome 사용: playwright.chromium.launch_persistent_context 대신 `chromium.launch(channel='chrome')` 혹은 `launch_persistent_context` + 실제 크롬 프로필이 더 자연스러움.
- HTTP/2 오류 회피: 과도한 `wait_until='networkidle'`은 장시간 H2 스트림을 열어두어 에러를 유발할 수 있음. `domcontentloaded` 후 필요한 요소만 기다리는 방식으로 변경.
- JS 비활성화 금지: 쿠팡은 JS 의존도가 높음. `--disable-javascript`는 탐지 리스크+기능 마비를 유발.
- 이미지/리소스 선택적 차단: `route`로 추적/광고 정도만 차단. 핵심 리소스는 허용.
- 지연과 인간행동: 무작위 스크롤, 마우스무브, dwell time 추가. 하지만 과하지 않게.
- 쿠키/세션 재사용: 로그인 필요 시 프로필 디렉터리 사용. 빈 세션보다 안정적.
- User-Agent/Accept-Language: ko-KR 설정 유지. 지역/언어 일관성.
- 오류 페이지 처리: "자동입력 방지"/"로봇이 아닙니다" 문자열 감지 시 백오프 및 세션 교체.

샘플 대기 전략

```python
await page.goto(url, wait_until='domcontentloaded')
await page.wait_for_selector('li.search-product, a.search-product-link')
```

리퀘스트 라우팅 예시

```python
async def route_handler(route):
    req = route.request
    if any(x in req.url for x in ['doubleclick', 'analytics', 'ads']):
        return await route.abort()
    return await route.continue_()

await context.route('**/*', route_handler)
```

기타
- viewport 고정 대신 `--start-maximized`로 실제 사용자 환경 유사화
- `permissions.query` 패치 등 난무하는 변조는 최소화: 과도하면 오히려 탐지됨
- 1 IP/1 세션 원칙 유지, 병렬성은 낮춰 안정성 우선
