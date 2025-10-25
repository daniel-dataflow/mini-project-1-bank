# 계좌 정보 클라스
class Account:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance

    #입금
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    # 출금
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    # 계좌 정보(메모리 주소가 아닌 문자열로 바로 나올 수 있게 __str__을 사용함)
    def __str__(self):
        return f"계좌번호: {self.account_number}, 잔액: {self.balance}원"

# 유저 정보를 가져오기 위한 클래스
class User:
    def __init__(self, name, user_id, password):
        self.name = name
        self.user_id = user_id
        self.password = password
        self.accounts = []

    # 계좌가 항목 읽어오기
    def add_account(self, account: Account):
        self.accounts.append(account)

    # 계좌 가져오기
    def get_account(self) -> Account:
        return self.accounts[0] if self.accounts else None

    # 비밀번호 체크
    def check_password(self, password_input):
        return self.password == password_input