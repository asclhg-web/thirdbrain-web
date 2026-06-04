import { getPermalink, getBlogPermalink } from './utils/permalinks';

// 외부 링크 (런칭 시 실제 주소로 교체)
const BOOKK_URL = '#'; // 부크크 구매 링크 자리
const TALLY_PROGRAM = getPermalink('/program') + '#apply'; // 30일 몰입 신청
const EEG_RESERVE = getPermalink('/eeg') + '#reserve'; // EEG 사전예약

export const headerData = {
  links: [
    { text: '홈', href: getPermalink('/') },
    { text: 'EEG', href: getPermalink('/eeg') },
    {
      text: '프로그램',
      links: [
        { text: '30일 몰입 프로그램', href: getPermalink('/program') + '#thirty' },
        { text: '서드브레인 부트캠프', href: getPermalink('/program') + '#bootcamp' },
      ],
    },
    { text: '자료실', href: getBlogPermalink() },
    { text: '소개', href: getPermalink('/about') },
  ],
  actions: [
    { text: '책 사기', href: BOOKK_URL, target: '_blank' },
    { text: 'EEG 사전예약', href: EEG_RESERVE },
    { text: '30일 몰입 시작', href: TALLY_PROGRAM, variant: 'primary' },
  ],
};

export const footerData = {
  links: [
    {
      title: '서드브레인',
      links: [
        { text: '세 번째 뇌란?', href: getPermalink('/#features') },
        { text: '책 소개', href: getPermalink('/#book') },
        { text: '추천사', href: getPermalink('/#testimonials') },
        { text: '책 사기', href: BOOKK_URL },
      ],
    },
    {
      title: '프로그램',
      links: [
        { text: '30일 몰입 프로그램', href: getPermalink('/program') + '#thirty' },
        { text: '서드브레인 부트캠프', href: getPermalink('/program') + '#bootcamp' },
        { text: 'EEG 몰입 측정', href: getPermalink('/eeg') },
        { text: 'EEG 사전예약', href: EEG_RESERVE },
      ],
    },
    {
      title: '둘러보기',
      links: [
        { text: '자료실', href: getBlogPermalink() },
        { text: '소개', href: getPermalink('/about') },
        { text: '자주 묻는 질문', href: getPermalink('/#faq') },
        { text: '문의', href: getPermalink('/about') + '#contact' },
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
