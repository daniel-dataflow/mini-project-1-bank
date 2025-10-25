# services.py - 은행 서비스 계층
from .models import User, Account
from .bank_storage import BankStorage
import random
from datetime import datetime

class BankService:
    def __init__(self, storage: BankStorage, log_storage: BankStorage = None):
        self.storage = storage
        self.log_storage = log_storage or BankStorage("transaction_log.json")
        self.users = self._load_users()
        self.current_user = None

    def _load_users(self):
        data = self.storage.load()
        users = {}
        for user_data in data.get('users', []):
            user = User(user_data['name'], user_data['id'], user_data['password'])
            for acc_dict in user_data.get('accounts', []):
                for acc_num, balance in acc_dict.items():
                    user.add_account(Account(acc_num, balance))
            users[user.user_id] = user
        return users

    def _save_users(self):
        data = {'users': []}
        for user in self.users.values():
            user_dict = {
                'name': user.name,
                'id': user.user_id,
                'password': user.password,
                'accounts': [{acc.account_number: acc.balance for acc in user.accounts}]
            }
            data['users'].append(user_dict)
        self.storage.save(data)

    def join(self, name, user_id, password):
        if user_id in self.users:
            return False, '이미 존재하는 ID입니다.'
        # 계좌번호 생성
        ac = '-'.join([
            '{0:04d}'.format(random.randint(0, 9999)),
            '{0:02d}'.format(random.randint(0, 99)),
            '{0:04d}'.format(random.randint(0, 9999))
        ])
        # 계좌번호 중복 체크
        for u in self.users.values():
            for acc in u.accounts:
                if acc.account_number == ac:
                    return False, '이미 존재하는 계좌번호입니다.'
        user = User(name, user_id, password)
        user.add_account(Account(ac, 0))
        self.users[user_id] = user
        self._save_users()
        return True, '회원가입 성공!'

    def login(self, user_id, password):
        user = self.users.get(user_id)
        if not user or not user.check_password(password):
            return False, 'ID 또는 비밀번호가 올바르지 않습니다.'
        self.current_user = user
        return True, f'{user.name}님 환영합니다!'

    def logout(self):
        self.current_user = None

    def create_account(self):
        if not self.current_user:
            return False, '로그인 후 이용하세요.'
        ac = '-'.join([
            '{0:04d}'.format(random.randint(0, 9999)),
            '{0:02d}'.format(random.randint(0, 99)),
            '{0:04d}'.format(random.randint(0, 9999))
        ])
        for u in self.users.values():
            for acc in u.accounts:
                if acc.account_number == ac:
                    return False, '이미 존재하는 계좌번호입니다.'
        self.current_user.add_account(Account(ac, 0))
        self._save_users()
        return True, f'신규 계좌({ac})가 생성되었습니다.'

    def deposit(self, account_number, amount):
        if not self.current_user:
            return False, '로그인 후 이용하세요.'
        acc = self.current_user.get_account(account_number)
        if not acc:
            return False, '계좌를 찾을 수 없습니다.'
        if acc.deposit(amount):
            self._save_users()
            return True, f'{amount}원 입금 완료.'
        return False, '입금 실패.'

    def withdraw(self, account_number, amount):
        if not self.current_user:
            return False, '로그인 후 이용하세요.'
        acc = self.current_user.get_account(account_number)
        if not acc:
            return False, '계좌를 찾을 수 없습니다.'
        if acc.withdraw(amount):
            self._save_users()
            return True, f'{amount}원 출금 완료.'
        return False, '출금 실패(잔액 부족 등).'

    def find_account_owner(self, account_number):
        for user in self.users.values():
            for account in user.accounts:
                if account.account_number == account_number:
                    return user, account
        return None, None

    def log_transaction(self, sender, recipient, amount):
        log_entry = {
            "type": "Account transfer",
            "sender_name": sender.name,
            "sender_account": sender.get_account().account_number,
            "recipient_name": recipient.name,
            "recipient_account": recipient.get_account().account_number,
            "amount": amount,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        logs = self.log_storage.load()
        if not isinstance(logs, list):
            logs = []
        logs.append(log_entry)
        self.log_storage.save(logs)

    def process_transfer(self, recipient, recipient_account, amount):
        my_account = self.current_user.get_account()
        print("\n------ 이체 정보 확인 ------")
        print(f"받는 분: {recipient.name}")
        print(f"받는 분 계좌번호: {recipient_account.account_number}")
        print(f"보내는 금액: {amount}원")
        print("----------------------------")
        for i in range(3):
            password = input("계좌 비밀번호를 입력해주세요: ")
            if self.current_user.check_password(password):
                if my_account.withdraw(amount) and recipient_account.deposit(amount):
                    self._save_users()
                    self.log_transaction(self.current_user, recipient, amount)
                    print("\n✅ 이체가 성공적으로 완료되었습니다.")
                    print(f"남은 잔액: {my_account.balance}원")
                    return True, "이체 완료"
                else:
                    print("\n❌ 오류: 잔액 변경 중 문제가 발생했습니다. 이체를 취소합니다.")
                    return False, "이체 실패"
            else:
                print(f"비밀번호가 틀렸습니다. (남은 기회 {2 - i}번)")
        print("❌ 비밀번호를 3회 이상 틀려 이체를 취소합니다.")
        return False, "비밀번호 오류"

    def get_transfer_amount(self, my_balance):
        while True:
            try:
                amount = int(input("이체하실 금액을 입력해 주세요 (숫자만): "))
                if amount <= 0:
                    print("0원 이하의 금액은 보낼 수 없습니다.")
                elif my_balance < amount:
                    print(f"잔액이 부족합니다. (최대: {my_balance}원)")
                else:
                    return amount
            except ValueError:
                print("숫자만 입력해주세요.")

    def get_recipient_info(self, my_account_number):
        while True:
            account_number = input("이체하실 계좌번호를 입력해 주세요: ")
            if account_number == my_account_number:
                print("자기 자신에게는 이체할 수 없습니다.")
                continue
            recipient, recipient_account = self.find_account_owner(account_number)
            if not recipient:
                print("없는 계좌번호 입니다. 다시 확인해 주세요.")
                continue
            check = input(f"받는 분 : {recipient.name} / 계좌: {recipient_account.account_number} 이 맞으신가요? (y/n): ").lower()
            if check == 'y':
                return recipient, recipient_account
            else:
                print("입력을 취소하고 다시 시도합니다.")

    def transfer(self):
        if not self.current_user:
            print('로그인 후 이용하세요.')
            return False, '로그인 필요'
        my_account = self.current_user.get_account()
        if not my_account:
            print('출금 계좌가 없습니다.')
            return False, '출금 계좌 없음'
        recipient, recipient_account = self.get_recipient_info(my_account.account_number)
        if not recipient:
            return False, '수취인 없음'
        amount = self.get_transfer_amount(my_account.balance)
        return self.process_transfer(recipient, recipient_account, amount)
