"""Odoo 어댑터 — 표준 XML-RPC (의존성 없음, 파이썬 내장).

설정은 .env 4줄이 전부 (어댑터 패턴 — 인스턴스가 바뀌어도 코드 불변):
  ODOO_URL=https://회사이름.odoo.com
  ODOO_DB=회사이름
  ODOO_USER=braingraph@...   (읽기 전용 전용 계정 권장)
  ODOO_API_KEY=...           (비밀번호 아님 — API 키. 채팅에 올리지 말 것)
"""
import os
import xmlrpc.client


def configured() -> bool:
    return all(os.environ.get(k) for k in
               ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY"))


class OdooClient:
    """지연 인증 XML-RPC 클라이언트. 실패는 예외로 — 호출부가 정직하게 알린다."""

    def __init__(self):
        self.url = os.environ.get("ODOO_URL", "").rstrip("/")
        self.db = os.environ.get("ODOO_DB", "")
        self.user = os.environ.get("ODOO_USER", "")
        self.key = os.environ.get("ODOO_API_KEY", "")
        self._uid = None

    def _common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)

    def _models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

    def uid(self) -> int:
        if self._uid is None:
            if not configured():
                raise RuntimeError("Odoo 미설정 — .env에 ODOO_URL/DB/USER/API_KEY 4줄이 필요합니다.")
            self._uid = self._common().authenticate(self.db, self.user, self.key, {})
            if not self._uid:
                raise RuntimeError("Odoo 인증 실패 — 계정/API 키를 확인하세요.")
        return self._uid

    def execute(self, model: str, method: str, args: list, kwargs: dict | None = None):
        return self._models().execute_kw(self.db, self.uid(), self.key,
                                         model, method, args, kwargs or {})

    def search_read(self, model: str, domain: list, fields: list, limit: int = 500) -> list[dict]:
        return self.execute(model, "search_read", [domain],
                            {"fields": fields, "limit": limit})

    def create(self, model: str, values: dict) -> int:
        return self.execute(model, "create", [values])

    def version(self) -> str:
        return str(self._common().version().get("server_version", "?"))


_OVERRIDE = None  # 테스트·모의용 클라이언트 주입점


def set_client(client) -> None:
    global _OVERRIDE
    _OVERRIDE = client


def get_client():
    return _OVERRIDE if _OVERRIDE is not None else OdooClient()
