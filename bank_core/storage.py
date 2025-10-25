
# storage.py - 데이터 저장/불러오기 담당
# 이 파일은 JSON 파일을 이용해 데이터를 영구적으로 저장/불러오는 기능을 제공합니다.

import json

class BankStorage:
    """
    데이터 저장소 클래스
    - bank.json 등 파일에 데이터를 저장/불러오기
    """
    def __init__(self, path="bank.json"):
        self.path = path  # 저장할 파일 경로

    def load(self) -> dict:
        """파일에서 데이터 불러오기. 없으면 빈 users 리스트 반환."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}

    def save(self, db) -> None:
        """데이터를 파일에 저장."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
