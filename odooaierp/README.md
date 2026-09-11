# odooaierp.com — AX 플랫폼 웹사이트

빌드 도구가 필요 없는 정적 원페이지 사이트입니다.

- `index.html` — 사이트 전체 (CSS 내장)
- `assets/` — 실제 구동 화면 4장 (승인함·근거 역추적·분석 스튜디오·War Room)
- `netlify.toml` — Netlify 배포 설정 (빌드 없음, 현재 폴더 그대로 게시)

## 배포 (Netlify 기준, 무료·HTTPS 자동)

1. https://app.netlify.com 가입 → **Add new site → Import an existing project** → GitHub에서 이 저장소 선택
2. 설정에서 **Base directory: `odooaierp`**, Build command: (비움), Publish directory: `odooaierp` 지정 → Deploy
3. 배포되면 `임의이름.netlify.app` 주소가 생깁니다 → **Domain settings → Add custom domain → `odooaierp.com`** 입력

간단 대안: netlify.com 로그인 후 **Deploys → 드래그&드롭**에 이 `odooaierp` 폴더를 통째로 끌어 놓아도 즉시 배포됩니다(이후 수정 시 다시 드롭).

## 아이네임즈(inames) DNS 설정

아이네임즈 로그인 → 도메인 관리 → `odooaierp.com` → **네임서버/DNS(호스트 IP) 관리**에서:

| 구분 | 호스트 | 값 |
|---|---|---|
| A 레코드 | @ (없음/루트) | `75.2.60.5` |
| CNAME | www | `<사이트이름>.netlify.app` |

- 저장 후 반영까지 보통 10분~1시간 (최대 24시간)
- 반영되면 Netlify가 자동으로 HTTPS(자물쇠) 인증서를 발급합니다
- Vercel을 쓸 경우: A `@` → `76.76.21.21`, CNAME `www` → `cname.vercel-dns.com`

## 수정 방법

`index.html` 텍스트를 고쳐 커밋(또는 다시 드래그&드롭)하면 끝입니다.
화면 이미지는 `assets/*.jpg` 교체.
