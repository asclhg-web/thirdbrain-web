// 외부 링크 — 관리자(Pages CMS)의 '홈 설정'에서 편집되는 home.json 에서 불러옵니다.
import home from './home.json';

export const LINKS = {
  bookk: home.links.bookk, // 부크크 등 책 구매 페이지 (1순위 행동)
  stibee: home.links.stibee, // 뉴스레터(스티비) 구독 (선택)
};
