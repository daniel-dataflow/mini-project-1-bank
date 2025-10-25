
# DB에서 값들을 불러오는 클래스
class BankUser:
    def __init__(self, storage, personal):
        self.storage = storage
        self.personal = personal

    # db 최신화
    def sync(self):
        return self.personal.db

    # 내부: 현재 로그인한 사용자 dict 찾기 (없으면 None)
    def _current_user(self):
        db = self.sync()
        uid = getattr(self.personal, "current_user_id", None)
        if uid is None:
            return None
        for u in db.get("users", []):
            if u.get("id") == uid:
                return u
        return None

    # users["id"] 값 반환
    def user_id(self):
        u = self._current_user()
        return u.get("id") if u else None

    # users["password"] 값 반환
    def user_password(self):
        u = self._current_user()
        return u.get("password")

    # users["name"] 값 반환
    def user_name(self):
        u = self._current_user()
        return u.get("name") if u else None

    # users["accounts"] 값 반환
    def user_accounts(self):
        u = self._current_user()
        return u.get("accounts", []) if u else []