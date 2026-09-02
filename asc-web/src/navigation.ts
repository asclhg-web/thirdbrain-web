import { getPermalink, getBlogPermalink } from './utils/permalinks';
import { LINKS } from './data/links';

export const headerData = {
  // 구성: 홈 · Odoo 컨설팅 · AI 지능화 기술 · 구축 서비스 · 책(▾) · 회사 소개 · 블로그 · 게시판 · [상담 신청]
  links: [
    { text: '홈', href: getPermalink('/') },
    { text: 'Odoo 컨설팅', href: getPermalink('/odoo') },
    { text: 'AI 지능화 기술', href: getPermalink('/ai') },
    { text: '구축 서비스', href: getPermalink('/services') },
    {
      text: '책',
      links: [
        { text: 'AI ERP 혁명 (신간)', href: getPermalink('/book') },
        { text: '서드브레인', href: getPermalink('/thirdbrain') },
      ],
    },
    { text: '회사 소개', href: getPermalink('/about') },
    { text: '블로그', href: getBlogPermalink() },
    { text: '게시판', href: getPermalink('/board') },
  ],
  actions: [{ text: '상담 신청', href: getPermalink('/about') + '#contact', variant: 'primary' }],
};

export const footerData = {
  links: [
    {
      title: '역량',
      links: [
        { text: 'Odoo 컨설팅 (모듈별)', href: getPermalink('/odoo') },
        { text: 'AI 지능화 기술 (온톨로지-지식그래프)', href: getPermalink('/ai') },
        { text: '구축 서비스·진행 절차', href: getPermalink('/services') },
        { text: '상담 신청', href: getPermalink('/about') + '#contact' },
      ],
    },
    {
      title: '책',
      links: [
        { text: '『Odoo를 중심으로 AI ERP 혁명』', href: getPermalink('/book') },
        { text: '『서드브레인』', href: getPermalink('/thirdbrain') },
        { text: 'AI ERP 혁명 구매 (교보)', href: LINKS.kyobo },
        { text: '서드브레인 구매 (교보)', href: LINKS.kyoboThirdbrain },
      ],
    },
    {
      title: '소식·회사',
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
  footNote: `(주)에이에스씨 · 대표 이형근 · Odoo Partner · 지사: 서울·경기 / 부산(영남) / 전라(나주) · 문의 asclhg@gmail.com`,
};
