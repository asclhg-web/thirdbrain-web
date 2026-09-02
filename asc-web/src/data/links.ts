// 외부 링크 — home.json 에서 관리
import home from './home.json';

export const LINKS = {
  kyobo: home.links.kyobo, // 『AI ERP 혁명』 교보 (출간 후 상품 URL로 교체)
  kyoboThirdbrain: home.links.kyoboThirdbrain, // 『서드브레인』 교보 상품
  email: `mailto:${home.links.email}`,
};
