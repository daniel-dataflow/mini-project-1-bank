import json

# 로드/세이브 기능 구현 클래스
class BankStorage:
    def __init__(self, path="bank.json"):
        self.path=path

    # 데이터 불러오기
    def load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}

    # 데이터 저장하기
    def save(self, db) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
