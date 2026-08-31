import { getPermalink, getBlogPermalink } from './utils/permalinks';
import { LINKS } from './data/links';

const KYOBO_URL = LINKS.kyobo; // 교보문고 구매 링크 (1순위 행동)

export const headerData = {
  // 구성: 홈 · 회사 소개 · Odoo AI ERP · 책 소개 · 블로그 · 게시판 · [책 구매]
  links: [
    { text: '홈', href: getPermalink('/') },
    { text: '회사 소개', href: getPermalink('/about') },
    { text: 'Odoo AI ERP', href: getPermalink('/odoo') },
    { text: '책 소개', href: getPermalink('/book') },
    { text: '블로그', href: getBlogPermalink() },
    { text: '게시판', href: getPermalink('/board') },
  ],
  actions: [{ text: '책 구매', href: KYOBO_URL, target: '_blank', variant: 'primary' }],
};

export const footerData = {
  links: [
    {
      title: '사업',
      links: [
        { text: 'Odoo 기반 지능형 ERP', href: getPermalink('/odoo') },
        { text: '온톨로지-지식그래프 AX', href: getPermalink('/odoo') + '#intelligence' },
        { text: '스마트공장·MES·IoT', href: getPermalink('/odoo') + '#ot' },
        { text: '컨설팅 문의', href: getPermalink('/about') + '#contact' },
      ],
    },
    {
      title: '책',
      links: [
        { text: '『AI ERP 혁명』 소개', href: getPermalink('/book') },
        { text: '목차 미리보기', href: getPermalink('/book') + '#toc' },
        { text: '저자 소개', href: getPermalink('/book') + '#authors' },
        { text: '책 구매 (교보문고)', href: KYOBO_URL },
      ],
    },
    {
      title: '소식',
      links: [
        { text: '블로그', href: getBlogPermalink() },
        { text: '게시판(공지)', href: getPermalink('/board') },
        { text: '회사 소개', href: getPermalink('/about') },
      ],
    },
  ],
  secondaryLinks: [
    { text: '이용약관', href: getPermalink('/terms') },
    { text: '개인정보처리방침', href: getPermalink('/privacy') },
  ],
  socialLinks: [{ ariaLabel: 'RSS', icon: 'tabler:rss', href: getPermalink('/rss.xml') }],
  footNote: `(주)에이에스씨 · ASC, AI System Creator · 전남 나주 — Odoo 기반 중소기업 지능형 ERP · 문의 ${'asclhg@gmail.com'}`,
};
