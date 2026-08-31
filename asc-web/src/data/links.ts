// 외부 링크 — home.json 에서 관리
import home from './home.json';

export const LINKS = {
  kyobo: home.links.kyobo, // 교보문고 책 구매 (1순위 행동)
  email: `mailto:${home.links.email}`,
};
