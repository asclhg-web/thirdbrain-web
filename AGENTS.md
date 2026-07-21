# AstroWind Agent Instructions

## Project Overview

AstroWind is a free, open-source website template built with **Astro v6** and **Tailwind CSS v4**. It generates a fully static site optimized for performance, SEO, and accessibility.

**Stack:** Astro v6 | Tailwind CSS v4 | TypeScript 5.9 | MDX | Sharp

## Quick Reference

| Command           | Purpose                             |
| ----------------- | ----------------------------------- |
| `npm run dev`     | Start dev server at localhost:4321  |
| `npm run build`   | Production build to `./dist/`       |
| `npm run preview` | Preview production build locally    |
| `npm run check`   | Run astro check + ESLint + Prettier |
| `npm run fix`     | Auto-fix ESLint + Prettier issues   |

**Node.js requirement:** >= 22.12.0

## Architecture

### Directory Structure

```
src/
  assets/styles/tailwind.css   # Tailwind v4 config (themes, utilities, plugins)
  components/
    common/        # Shared: Image, Metadata, Analytics, ToggleTheme
    ui/            # Primitives: Button, Headline, WidgetWrapper, ItemGrid
    widgets/       # Page sections: Hero, Features, Pricing, Header, Footer
    blog/          # Blog: SinglePost, List, Pagination, Tags
    CustomStyles.astro  # CSS variables for colors and fonts
  content.config.ts    # Content Collections schema (Astro v6 location)
  data/post/           # Blog posts (.md, .mdx)
  layouts/             # Layout.astro, PageLayout.astro, MarkdownLayout.astro
  pages/               # File-based routing
  utils/               # blog.ts, images.ts, permalinks.ts, frontmatter.ts
  config.yaml          # Site configuration (loaded as virtual module)
  navigation.ts        # Navigation structure
  types.d.ts           # TypeScript type definitions
vendor/integration/    # Custom Astro integration for config loading
```

### Path Aliases

Use `~/` to import from `src/`:

```typescript
import Image from '~/components/common/Image.astro';
import { SITE } from 'astrowind:config';
```

### Configuration System

Site config lives in `src/config.yaml` and is loaded as a Vite virtual module `astrowind:config` by the custom integration in `vendor/integration/`. Exports: `SITE`, `I18N`, `METADATA`, `APP_BLOG`, `UI`, `ANALYTICS`.

## Tailwind CSS v4

Configuration is CSS-first in `src/assets/styles/tailwind.css`:

- **Theme tokens:** `@theme { --color-primary: var(--aw-color-primary); ... }`
- **Custom utilities:** `@utility bg-page { ... }`
- **Dark mode:** Class-based via `@variant dark (&:where(.dark, .dark *))`
- **Plugins:** `@plugin "@tailwindcss/typography"`
- **Custom variant:** `@custom-variant intersect (&:not([no-intersect]))`

CSS variables for colors/fonts are defined in `src/components/CustomStyles.astro` with light/dark theme variants.

The Vite plugin `@tailwindcss/vite` is configured in `astro.config.ts` (not as an Astro integration).

### Class Merging

Components use `twMerge` from `tailwind-merge` v3 for conditional class composition.

## Content Collections

Defined in `src/content.config.ts` using the Astro v6 Content Layer API with `glob()` loader. Posts are in `src/data/post/` as `.md` or `.mdx` files.

Post frontmatter: `title` (required), `publishDate`, `updateDate`, `draft`, `excerpt`, `image`, `category`, `tags`, `author`, `metadata`.

## Component Patterns

- Props extend interfaces from `~/types`
- Use `class:list` for conditional classes
- Use `twMerge()` when accepting className overrides
- Use named slots for layout composition
- Widget components accept standardized props (see `~/types`)

## Image Handling

`src/components/common/Image.astro` supports:

- Local images via `astro:assets` (optimized by Sharp)
- Remote images via Unpic CDN
- Allowed domains (for providers Unpic can't detect, processed by Sharp): `cdn.pixabay.com`

Hero images use `loading="eager"` and `fetchpriority="high"`.

## Verification Checklist

After changes, always verify:

1. `npm run build` succeeds
2. `npm run check` passes (astro check + ESLint + Prettier)
3. Visual check in browser: homepage, blog, dark mode, mobile menu

---

# 브레인그래프(BrainGraph) 프로젝트 메모리

이 저장소의 진짜 프로젝트는 웹 템플릿이 아니라 **브레인그래프 — Physical AI 로봇의
지능을 만드는 개인·기업 통합 온톨로지 지식그래프 플랫폼**이다 (`physical-brain/`,
`book/draft-v2/`).

## 최상위 문서 (이 순서로 우선한다)

1. `book/draft-v2/브레인그래프_유산헌장.docx` — 프로젝트 헌법. 북극성: 주인이 평생
   기른 그래프를 딸에게 유산으로 물려주는 것. 제1원칙 "언제 멈춰도 선물이 되도록".
2. `book/draft-v2/브레인그래프_플랫폼_제안서_v2.docx` — 마스터 체계(몸·학습·일·마음),
   G01~G20 WBS.
3. `book/draft-v2/온톨로지지식그래프_방법론_KG-DMAIC_v2.docx` — 구축 방법론.

## 개발 시 필수

**브레인그래프·피지컬브레인 관련 개발/설계 전에 반드시 `braingraph-philosophy` 스킬을
참조할 것.** 핵심만 요약하면: 진실의 원본은 볼트/Odoo(그래프는 거울), 미확인은
미확인으로, Frame/Instance 분리, CQ 주도 설계, HITL 승인, 어댑터 패턴, 마크다운·
SQLite 기본(데이터 주권), 매 턴 테스트+커밋+푸시. 기능과 상속 가능성이 충돌하면
상속 가능성이 이긴다.

사용자는 비개발자(경영컨설턴트·저자·Odoo 파트너)이며, 안내는 복사-붙여넣기 명령
단위로 제공한다. 서버: DESKTOP-ACK17CB(Windows, RTX 5080, 포트 8810, 주식학습
19:00~05:30과 GPU 동거).
