from datetime import datetime
from bank_transfer_models import User, Account
from bank_storage import BankStorage


class BankService:

    # 서비스 초기화 시 데이터 저장을 담당하는 storage 객체들을 전달(의존성 주입)
    def __init__(self, bank_storage: BankStorage, log_storage: BankStorage):
        self.bank_storage = bank_storage
        self.log_storage = log_storage
        self.users = {}
        self.object_users()  # 데이터를 객체로 변환
        self.current_user = list(self.users.values())[0] if self.users else None

    # 사용을 위한 객체화
    def object_users(self):
        data = self.bank_storage.load()

        for user_data in data.get('users', []):
            user = User(user_data['name'], user_data['id'], user_data['password'])
            for acc_dict in user_data.get('accounts', []):
                for acc_num, balance in acc_dict.items():
                    user.add_account(Account(acc_num, balance))
            self.users[user.user_id] = user

    # 저장을 위한 dictionary 형태로 변환
    def dict_data(self) -> dict:
        data_to_save = {'users': []}
        for user in self.users.values():
            user_dict = {
                'name': user.name,
                'id': user.user_id,
                'password': user.password,
                'accounts': [{acc.account_number: acc.balance for acc in user.accounts}]
            }
            data_to_save['users'].append(user_dict)
        return data_to_save

    # 받을 사람 계좌 일치여부
    def find_account_owner(self, account_number):
        """계좌번호로 해당 계좌와 소유자(User)를 함께 찾아 반환합니다."""
        for user in self.users.values():
            for account in user.accounts:
                if account.account_number == account_number:
                    return user, account
        return None, None

    def run(self):
        """이체 서비스의 전체 프로세스를 실행합니다."""
        if not self.current_user:
            print("오류: 로그인된 사용자 정보가 없습니다.")
            return

        my_account = self.current_user.get_account()
        if not my_account:
            print("오류: 현재 사용자의 계좌 정보가 없습니다.")
            return

        print("====== 세종 은행 이체 서비스 ======")
        print(f"안녕하세요, {self.current_user.name}님!")
        print(f"주 계좌: {my_account.account_number}")
        print(f"현재 잔액: {my_account.balance}원")
        print("==============================")

        recipient, recipient_account = self.get_recipient_info(my_account.account_number)
        if not recipient:
            return

        amount = self.get_transfer_amount(my_account.balance)
        self.process_transfer(recipient, recipient_account, amount)

    # 이체할 대상자 입력
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

    # 이체할 금액 체크
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

    # 성공한 경우 JSON에 이체기록을 남김
    def log_transaction(self, sender: User, recipient: User, amount):
        log_entry = {
            "type" : "Account transfer",
            "sender_name": sender.name,
            "sender_account": sender.get_account().account_number,
            "recipient_name": recipient.name,
            "recipient_account": recipient.get_account().account_number,
            "amount": amount,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        logs = self.log_storage.load()  # 로그 불러오기
        if not isinstance(logs, list):  # 로그가 없으면 리스트 만들기
            logs = []

        logs.append(log_entry)          # 로그 추가
        self.log_storage.save(logs)     # 저장하기

    # 패스워드가 맞으면 실제 처리를 담당
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
                    # 객체 상태를 dict로 변환 후 storage에 저장을 위임
                    data_to_save = self.dict_data()
                    self.bank_storage.save(data_to_save)

                    self.log_transaction(self.current_user, recipient, amount)
                    print("\n\n====== 세종 은행 이체 서비스 ======")
                    print("✅ 이체가 성공적으로 완료되었습니다.")
                    print(f"남은 잔액: {my_account.balance}원")
                    print("===== 이용해 주셔서 감사합니다. =====")
                    return
                else:
                    print("\n❌ 오류: 잔액 변경 중 문제가 발생했습니다. 이체를 취소합니다.")
                    return
            else:
                print(f"비밀번호가 틀렸습니다. (남은 기회 {2 - i}번)")

        print("❌ 비밀번호를 3회 이상 틀려 이체를 취소합니다.")