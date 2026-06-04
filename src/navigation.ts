import { getPermalink, getBlogPermalink } from './utils/permalinks';
import { LINKS } from './data/links';

// 외부 링크 (실제 주소는 src/data/links.ts 에서 관리)
const BOOKK_URL = LINKS.bookk; // 부크크 구매 링크 (1순위 행동)
const TALLY_PROGRAM = getPermalink('/program') + '#apply'; // 30일 몰입 신청
const EEG_RESERVE = getPermalink('/eeg') + '#reserve'; // EEG 프로젝트 사전예약

export const headerData = {
  // 우선순위 순서: 책 → 프로그램(부록) → EEG(프로젝트)
  links: [
    { text: '홈', href: getPermalink('/') },
    { text: '책 소개', href: getPermalink('/#book') },
    {
      text: '프로그램',
      links: [
        { text: '30일 몰입 프로그램', href: getPermalink('/program') + '#thirty' },
        { text: '서드브레인 부트캠프', href: getPermalink('/program') + '#bootcamp' },
      ],
    },
    { text: 'EEG 프로젝트', href: getPermalink('/eeg') },
    { text: '자료실', href: getBlogPermalink() },
    { text: '소개', href: getPermalink('/about') },
  ],
  // 헤더 버튼: '책 구매'를 1순위(primary)로
  actions: [
    { text: '30일 몰입', href: TALLY_PROGRAM },
    { text: '책 구매', href: BOOKK_URL, target: '_blank', variant: 'primary' },
  ],
};

export const footerData = {
  links: [
    {
      title: '책 (1순위)',
      links: [
        { text: '책 소개', href: getPermalink('/#book') },
        { text: '세 개의 뇌', href: getPermalink('/#features') },
        { text: '추천사', href: getPermalink('/#testimonials') },
        { text: '책 구매', href: BOOKK_URL },
      ],
    },
    {
      title: '부록 · 프로그램',
      links: [
        { text: '30일 몰입 프로그램', href: getPermalink('/program') + '#thirty' },
        { text: '서드브레인 부트캠프', href: getPermalink('/program') + '#bootcamp' },
        { text: '30일 몰입 신청', href: TALLY_PROGRAM },
      ],
    },
    {
      title: 'EEG 프로젝트',
      links: [
        { text: 'EEG 수면·인지개선', href: getPermalink('/eeg') },
        { text: '프로젝트 사전예약', href: EEG_RESERVE },
        { text: '자료실', href: getBlogPermalink() },
        { text: '소개', href: getPermalink('/about') },
      ],
    },
  ],
  secondaryLinks: [
    { text: '이용약관', href: getPermalink('/terms') },
    { text: '개인정보처리방침', href: getPermalink('/privacy') },
  ],
  socialLinks: [],
  footNote: `
    <span class="font-semibold">서드브레인</span> · 몸 · 지식 · AI를 잇는 새로운 뇌경영 · © 2026 이형근. All rights reserved.
  `,
};
