# asc-web — 에이에스씨(asc.kr) 홈페이지

서드브레인 웹사이트(AstroWind/Astro 6 + Tailwind 4)를 기반으로 만든 (주)에이에스씨 회사 홈페이지.

## 페이지 구성
- `/` 홈 — 회사 슬로건·사업영역·방법론·책 미리보기
- `/about` 회사 소개 — 문제의식·서비스 형태·진행 절차·팀·연락처
- `/odoo` Odoo AI ERP — IT·지능화·OT 3계층 아키텍처와 도입 로드맵
- `/book` 책 소개 — 『AI ERP 혁명 — Odoo와 지능형 ERP』 랜딩
- `/blog` 블로그 — `src/data/post/*.md` 마크다운 글
- `/board` 게시판 — `src/pages/board.astro` 상단 `notices` 배열에 글 추가
- 헤더 [책 구매] 버튼 — `src/data/home.json`의 `links.kyobo` 링크

## 개발·빌드
```bash
npm ci
npm run dev     # 개발 서버
npm run build   # dist/ 정적 빌드
```

## 배포 (asc.kr)
정적 사이트이므로 Netlify/Vercel/Cloudflare Pages 어디든 가능.
1. 이 폴더를 배포 대상으로 지정 (base directory: `asc-web`, build: `npm run build`, publish: `dist`)
2. 도메인 asc.kr 연결 (DNS A/CNAME → 호스팅 안내에 따름)
3. `src/config.yaml`의 `site: 'https://asc.kr'` 이 이미 설정되어 있음
