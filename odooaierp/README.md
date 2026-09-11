# odooaierp.com — AX 플랫폼 웹사이트 + 라이브 데모

빌드 도구가 필요 없는 정적 사이트입니다. 서버 없이도 데모가 동작합니다.

- `index.html` — 소개 페이지 (히어로·구조·실화면·성과·로드맵·문의)
- `demo/index.html` — **라이브 데모**: 실제 파이프라인 산출 데이터(판단 카드 5건·감사 로그·브리핑)가
  내장되어 브라우저 안에서 승인·반려·근거 역추적·War Room 갱신이 실제로 동작
- `assets/` — 실제 구동 화면 4장

## 배포 — Cloudflare Pages (기존 asc.kr 관리하는 그 계정에서, 추가 비용 없음)

1. Cloudflare 대시보드 → **Workers & Pages → Create → Pages → Upload assets**
   → 이 `odooaierp` 폴더를 통째로 업로드 (또는 *Connect to Git*으로 이 저장소 연결,
   Build command 비움, Build output directory: `odooaierp`)
2. 배포되면 `프로젝트명.pages.dev` 주소가 생깁니다 — 여기까지로 데모 리허설 가능

## 도메인 연결 — odooaierp.com (아이네임즈 구입분)

asc.kr과 같은 방식으로 Cloudflare에서 관리하게 만드는 것이 가장 깔끔합니다:

1. Cloudflare 대시보드 → **Add a site → `odooaierp.com`** (Free 플랜이면 충분)
2. Cloudflare가 알려주는 **네임서버 2개**(예: `xxx.ns.cloudflare.com`)를 복사
3. 아이네임즈 로그인 → 도메인 관리 → `odooaierp.com` → **네임서버 변경**에 붙여넣기
4. 반영(수 분~수 시간) 후 Cloudflare에서 도메인이 Active가 되면:
   **Workers & Pages → 해당 프로젝트 → Custom domains → `odooaierp.com` 추가**
   (DNS 레코드·HTTPS 인증서는 Cloudflare가 자동 구성)

이후 `www.odooaierp.com`도 Custom domains에 추가하면 함께 동작합니다.

## 데모 시나리오 (사이트에서 시연)

1. 브라우저에 **odooaierp.com** 입력 → 히어로에서 **▶ 라이브 데모 바로 실행**
2. 승인함에서 카드 1건 **왜?(근거)** → 근거 사다리 → **승인 → 환류**
3. **감사 로그 · 환류** 탭 — 방금 결정이 노란 행으로 기록된 것 확인
4. **War Room** 탭 — 처리율·승인율이 방금 승인으로 바뀐 것 확인
5. 우상단 **시연 초기화**로 언제든 처음 상태로 복원 (상태는 관람자 브라우저에만 저장)

## 수정 방법

- 문구: `index.html` 편집 후 재업로드(또는 커밋)
- 데모 데이터 갱신: 저장소의 `scratchpad/build_webdemo.py`가 `demo_data.json`으로부터
  `demo/index.html`을 재생성 — 플랫폼 재실행 후 데이터만 다시 추출하면 됩니다
