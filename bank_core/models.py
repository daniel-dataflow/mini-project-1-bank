
# models.py - 은행 시스템의 핵심 데이터 모델
# 이 파일은 계좌(Account)와 사용자(User) 객체를 정의합니다.

class Account:
    """
    계좌 클래스
    - 계좌번호, 잔액, 입금/출금 기능 제공
    """
    def __init__(self, account_number, balance=0):
        self.account_number = account_number  # 계좌번호 (문자열)
        self.balance = balance                # 잔액 (정수)

    def deposit(self, amount):
        """입금 기능. 양수만 가능."""
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        """출금 기능. 잔액 내에서만 가능."""
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def __str__(self):
        """계좌 정보 출력용 문자열."""
        return f"계좌번호: {self.account_number}, 잔액: {self.balance}원"


class User:
    """
    사용자 클래스
    - 이름, ID, 비밀번호, 계좌 목록 관리
    """
    def __init__(self, name, user_id, password):
        self.name = name                  # 사용자 이름
        self.user_id = user_id            # 사용자 ID
        self.password = password          # 비밀번호
        self.accounts = []                # 계좌(Account) 객체 리스트

    def add_account(self, account: Account):
        """계좌 추가 기능."""
        self.accounts.append(account)

    def get_account(self, account_number=None):
        """계좌번호로 계좌 찾기. 없으면 첫 번째 계좌 반환."""
        if account_number is None:
            return self.accounts[0] if self.accounts else None
        for acc in self.accounts:
            if acc.account_number == account_number:
                return acc
        return None

    def check_password(self, password_input):
        """비밀번호 일치 여부 확인."""
        return self.password == password_input
