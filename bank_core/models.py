# models.py - 은행 시스템의 핵심 데이터 모델

class Account:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False
    def __str__(self):
        return f"계좌번호: {self.account_number}, 잔액: {self.balance}원"

class User:
    def __init__(self, name, user_id, password):
        self.name = name
        self.user_id = user_id
        self.password = password
        self.accounts = []  # Account 객체 리스트
    def add_account(self, account: Account):
        self.accounts.append(account)
    def get_account(self, account_number=None):
        if account_number is None:
            return self.accounts[0] if self.accounts else None
        for acc in self.accounts:
            if acc.account_number == account_number:
                return acc
        return None
    def check_password(self, password_input):
        return self.password == password_input
