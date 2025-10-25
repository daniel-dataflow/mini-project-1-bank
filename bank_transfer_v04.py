import json
import sys


# --- 데이터 모델 클래스 ---

class Account:
    """계좌의 정보와 기능을 관리하는 클래스"""

    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        """입금: 잔액을 증가시킵니다."""
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        """출금: 잔액을 감소시킵니다."""
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def __str__(self):
        """객체를 출력할 때의 형식을 지정합니다."""
        return f"계좌번호: {self.account_number}, 잔액: {self.balance}원"


class User:
    """사용자 정보와 계좌 목록을 관리하는 클래스"""

    def __init__(self, name, user_id, password):
        self.name = name
        self.user_id = user_id
        self.__password = password
        self.accounts = []

    def add_account(self, account: Account):
        """사용자에게 계좌를 추가합니다."""
        self.accounts.append(account)

    def get_primary_account(self) -> Account:
        """사용자의 주 계좌(첫 번째 계좌)를 반환합니다."""
        return self.accounts[0] if self.accounts else None

    def check_password(self, password_input):
        """입력된 비밀번호가 맞는지 확인합니다."""
        return self.__password == password_input


# --- 서비스 제어 클래스 ---

class BankService:
    """은행 이체 서비스를 총괄하고 실행 흐름을 제어하는 클래스"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.users = {}  # user_id를 key로 User 객체를 저장
        self._load_data()
        self.current_user = list(self.users.values())[0]  # 첫 번째 사용자를 로그인 상태로 가정

    def _load_data(self):
        """JSON 파일에서 데이터를 로드하여 User와 Account 객체를 생성합니다."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for user_data in data.get('users', []):
                user = User(user_data['name'], user_data['id'], user_data['password'])
                for acc_dict in user_data.get('accounts', []):
                    for acc_num, balance in acc_dict.items():
                        user.add_account(Account(acc_num, balance))
                self.users[user.user_id] = user

        except FileNotFoundError:
            print(f"오류: '{self.filepath}' 파일을 찾을 수 없습니다.")
            sys.exit()  # 프로그램 종료

    def _save_data(self):
        """현재 객체 상태를 JSON 파일에 다시 저장합니다."""
        data_to_save = {'users': []}
        for user in self.users.values():
            user_dict = {
                'name': user.name,
                'id': user.user_id,
                'password': user._User__password,  # Private 변수 접근
                'accounts': [{acc.account_number: acc.balance for acc in user.accounts}]
            }
            data_to_save['users'].append(user_dict)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def find_account_owner(self, account_number):
        """계좌번호로 해당 계좌와 소유자(User)를 함께 찾아 반환합니다."""
        for user in self.users.values():
            for account in user.accounts:
                if account.account_number == account_number:
                    return user, account
        return None, None

    def run(self):
        """이체 서비스의 전체 프로세스를 실행합니다."""
        my_account = self.current_user.get_primary_account()
        if not my_account:
            print("오류: 현재 사용자의 계좌 정보가 없습니다.")
            return

        print("====== 세종 은행 이체 서비스 ======")
        print(f"안녕하세요, {self.current_user.name}님!")
        print(f"주 계좌: {my_account.account_number}")
        print(f"현재 잔액: {my_account.balance}원")
        print("==============================")

        # 1. 받는 사람 정보 입력
        recipient, recipient_account = self._get_recipient_info(my_account.account_number)
        if not recipient:
            return

        # 2. 보낼 금액 입력
        amount = self._get_transfer_amount(my_account.balance)

        # 3. 이체 실행 및 최종 확인
        self._process_transfer(recipient, recipient_account, amount)

    def _get_recipient_info(self, my_account_number):
        """사용자로부터 수신자 정보를 입력받는 내부 메서드"""
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

    def _get_transfer_amount(self, my_balance):
        """사용자로부터 이체 금액을 입력받는 내부 메서드"""
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

    def _process_transfer(self, recipient, recipient_account, amount):
        """실제 이체 로직을 처리하는 내부 메서드"""
        my_account = self.current_user.get_primary_account()

        print("\n------ 이체 정보 확인 ------")
        print(f"받는 분: {recipient.name}")
        print(f"받는 분 계좌번호: {recipient_account.account_number}")
        print(f"보내는 금액: {amount}원")
        print("----------------------------")

        for i in range(3):
            password = input("계좌 비밀번호를 입력해주세요: ")
            if self.current_user.check_password(password):
                # 출금과 입금이 모두 성공해야 이체 완료
                if my_account.withdraw(amount) and recipient_account.deposit(amount):
                    self._save_data()  # 성공 시에만 파일에 저장
                    print("\n✅ 이체가 성공적으로 완료되었습니다.")
                    print(f"남은 잔액: {my_account.balance}원")
                    return
                else:
                    # 로직상 실패할 확률은 적지만, 만약을 위한 방어 코드
                    print("\n❌ 오류: 잔액 변경 중 문제가 발생했습니다. 이체를 취소합니다.")
                    # 여기서 원상복구(rollback) 로직이 필요할 수 있음
                    return
            else:
                print(f"비밀번호가 틀렸습니다. (남은 기회 {2 - i}번)")

        print("❌ 비밀번호를 3회 이상 틀려 이체를 취소합니다.")


# --- 프로그램 실행 ---

if __name__ == "__main__":
    bank_service = BankService("../bank.json")
    bank_service.run()