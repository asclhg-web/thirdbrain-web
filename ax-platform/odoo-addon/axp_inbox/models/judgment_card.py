# 판단 카드 프록시 모델 — 원본은 AX 플랫폼(axp-api). Odoo에는 캐시·화면·권한만.
import json
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


def _api_base(env):
    return env["ir.config_parameter"].sudo().get_param(
        "axp_inbox.api_base", "http://axp-api:8000")


def _api_headers(env, extra=None):
    """P5-S6: 플랫폼 API 공유 키(설정 시) — axp_inbox.api_key 파라미터."""
    h = dict(extra or {})
    key = env["ir.config_parameter"].sudo().get_param("axp_inbox.api_key", "")
    if key:
        h["X-API-Key"] = key
    return h


class AxpJudgmentCard(models.Model):
    _name = "axp.judgment.card"
    _description = "AX 판단 카드"
    _order = "platform_id desc"

    platform_id = fields.Integer("플랫폼 카드 ID", required=True, index=True)
    kind = fields.Selection([
        ("demand_forecast", "수요예측"), ("replenish", "보충 정책"),
        ("allocation", "배분"), ("production_plan", "생산계획"),
        ("equip_alert", "설비경보"), ("knowledge", "지식 승격"), ("sop_revision", "SOP 개정")],
        string="유형", required=True)
    agent = fields.Char("에이전트")
    proposal = fields.Text("제안", required=True)
    narrative = fields.Text("설명(전 문장 근거 인용)")
    values_json = fields.Text("수치(JSON)")
    range_json = fields.Char("구간(JSON)")
    alternatives_json = fields.Text("대안(JSON)")
    evidence_text = fields.Text("근거 경로", readonly=True)
    state = fields.Selection([
        ("proposed", "제안됨"), ("review", "검토중"), ("approved", "승인"),
        ("rejected", "반려"), ("executed", "실행"), ("feedback", "환류")],
        default="proposed", string="상태", index=True)
    reject_reason = fields.Selection([
        ("수치 의문", "수치 의문"), ("근거 부족", "근거 부족"),
        ("시점 부적절", "시점 부적절"), ("현장 사정", "현장 사정"),
        ("대안 선호", "대안 선호"), ("기타", "기타")], string="반려 사유")
    reject_note = fields.Text("반려 상세")

    _sql_constraints = [
        ("platform_id_uniq", "unique (platform_id)", "이미 동기화된 카드입니다."),
    ]

    # ── 동기화(크론): 플랫폼의 대기 카드 → Odoo 화면 ─────────────────
    @api.model
    def cron_sync(self):
        base = _api_base(self.env)
        try:
            rows = requests.get(f"{base}/cards", headers=_api_headers(self.env), timeout=10).json()
        except requests.RequestException as e:
            _logger.warning("axp-api 접속 실패: %s", e)
            return
        n_ok = n_fail = 0
        for r in rows:
            # P3-I4: 한 카드의 값 오류(예: 미등록 kind)가 전체 동기화를 죽이면
            # 안 된다 — 행 단위 savepoint 로 격리하고 나머지는 계속 간다.
            try:
                with self.env.cr.savepoint():
                    rec = self.search([("platform_id", "=", r["card_id"])], limit=1)
                    vals = {
                        "platform_id": r["card_id"], "kind": r["kind"], "agent": r["agent"],
                        "proposal": r["proposal"], "narrative": r.get("narrative"),
                        "values_json": r.get("values_json"), "range_json": r.get("range_json"),
                        "alternatives_json": r.get("alternatives_json"), "state": r["status"],
                    }
                    if rec:
                        rec.write({"state": r["status"]})
                    else:
                        self.create(vals)
                    n_ok += 1
            except Exception as e:  # noqa: BLE001
                n_fail += 1
                _logger.warning("카드 #%s 동기화 실패(건너뜀): %s", r.get("card_id"), e)
        if n_fail:
            _logger.warning("판단 카드 동기화: 성공 %s · 실패 %s", n_ok, n_fail)

    # ── '왜?' — 근거 경로 (M5-3) ─────────────────────────────────
    def action_why(self):
        self.ensure_one()
        base = _api_base(self.env)
        res = requests.get(f"{base}/cards/{self.platform_id}/why", headers=_api_headers(self.env), timeout=10).json()
        self.evidence_text = res.get("text") or json.dumps(
            res, ensure_ascii=False, indent=2)

    # ── 승인/반려 — card_approver 그룹만, 결정은 플랫폼 API가 집행 ────
    def _decide(self, approve: bool):
        self.ensure_one()
        if not self.env.user.has_group("axp_inbox.group_card_approver"):
            raise AccessError("판단 카드 승인 권한(card_approver)이 없습니다.")
        base = _api_base(self.env)
        params = {"approve": approve, "actor": self.env.user.name,
                  "reason_code": self.reject_reason or "",
                  "reason_text": self.reject_note or ""}
        resp = requests.post(f"{base}/cards/{self.platform_id}/decide",
                             params=params, headers=_api_headers(self.env, {"X-Role": "card_approver"}),
                             timeout=15)
        if resp.status_code != 200:
            raise UserError(f"플랫폼 응답 오류: {resp.status_code} {resp.text[:200]}")
        self.state = resp.json().get("status", self.state)

    def action_approve(self):
        self._decide(True)

    def action_reject(self):
        if not self.reject_reason:
            raise UserError("반려 사유를 먼저 선택하세요 — 사유는 재학습 재료가 됩니다.")
        self._decide(False)
