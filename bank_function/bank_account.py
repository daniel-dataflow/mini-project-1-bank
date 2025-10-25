import random
from .bank_user import BankUser
from datetime import datetime
from bank_transfer_services import BankService
from bank_storage import BankStorage

# 계좌 관련 클래스
class BankAccount:
    def __init__(self, storage, personal):
        self.storage = storage
        self.personal = personal
        self.user = BankUser(storage, personal)


    # db 최신화
    def _sync(self):
        self.personal.db = self.storage.load()
        return self.personal.db


    # 로그인 여부 검증
    def _require_login(self):
        if not self.personal.current_login:
            print("로그인 후 이용 가능합니다.")
            return False
        return True


    # 계좌 조회
    def search(self, personal):
        if not self._require_login():
            return False
        self._sync()

        # 이름/계좌 호출
        name = self.user.user_name()
        accounts = self.user.user_accounts()

        # name없으면 오류
        if not name:
            print("로그인이 필요합니다.")
            return False

        # 계좌 없으면 발생
        if not accounts:
            print("등록된 계좌가 없습니다.")
            return False

        # 계좌 목록 확인
        print(f"\n[{name}]님의 계좌 목록: ")
        for ac in accounts:
            for ac_no, balance in ac.items():
                print(f"- {ac_no}: {balance}원")


    # 계좌 개설
    def new_account(self, personal):
        if not self._require_login():
            return False
        db = self._sync()

        # id/계좌 호출
        id = self.user.user_id()
        accounts = self.user.user_accounts()

        # user없으면 오류
        if not id:
            print("로그인이 필요합니다.")
            return False

        # "0000-00-0000" 계좌 추가(중복 방지)
        while True:
            ac_list = [
                f"{random.randint(0, 9999):04d}",
                f"{random.randint(0, 99):02d}",
                f"{random.randint(0, 9999):04d}",
            ]
            ac = '-'.join(map(str, ac_list))
            if not self.personal.account_exists(ac):
                break

        # 사용자 계좌에 추가
        accounts.append({ac : 0})
        self.storage.save(db)
        print(f"새 계좌가 생성되었습니다. 계좌번호: {ac}")
        return True


    # 계좌 삭제
    def delete_account(self, personal):
        if not self._require_login():
            return False
        db = self._sync()

        # 계좌 호출
        accounts = self.user.user_accounts()

        if not accounts:
            print("삭제할 계좌가 없습니다.")
            return False

        print("\n[계좌 조회]")
        self.search(personal)

        ac_number = input("삭제할 계좌번호를 입력하세요: ").strip()

        for account_dict in accounts:
            if ac_number in account_dict:
                bal = account_dict[ac_number]
                if bal > 0:
                    c = input("잔액이 남아 있습니다. 그래도 삭제하시겠습니까? (y/N): ").lower()
                    if c != 'y':
                        print("삭제를 취소했습니다.")
                        return False
                accounts.remove(account_dict)
                self.storage.save(db)
                print(f"계좌 {ac_number}가 삭제되었습니다.")
                return True

        print("해당 계좌번호를 찾을 수 없습니다.")
        return False


    # 계좌 이체
    def transfer_account(self, personal):
        if not self._require_login():
            return False
        db = self._sync()

        main_db_storage = BankStorage(path="bank.json")
        log_db_storage = BankStorage(path="transaction_log.json")

        # 2. Bank_Service
        bank_service = BankService(
            bank_storage=main_db_storage,
            log_storage=log_db_storage
        )

        # 3. 서비스를 실행합니다.
        bank_service.run()
# ===============================================================
        # 이름/계좌/pw 호출
        name = self.user.user_name()
        accounts = self.user.user_accounts()
        password = self.user.user_password()

        # 내 계좌 목록을 화면에 보여주고, 선택할 수 있도록 준비
        print("\n[내 계좌]")
        my_list = []  # [(계좌번호, 잔액, 해당계좌딕셔너리), ...] 형태로 평탄화 보관

        for i, account in enumerate(accounts, 1):
            # account는 {"123-45-678901": 10000} 같은 구조
            for num, bal in account.items():
                print(f"{i}. {num} | 잔액: {bal}원")
                my_list.append((num, bal, account))

        # 계좌가 하나도 없으면 이체 불가
        if not my_list:
            print("보유한 계좌가 없습니다.")
            return False

    """
    def transfer_account(self, personal):
        if not self._require_login():
            return False
        db = self._sync()

        # 이름/계좌/pw 호출
        name = self.user.user_name()
        accounts = self.user.user_accounts()
        password = self.user.user_password()

        # 내 계좌 목록을 화면에 보여주고, 선택할 수 있도록 준비
        print("\n[내 계좌]")
        my_list = []  # [(계좌번호, 잔액, 해당계좌딕셔너리), ...] 형태로 평탄화 보관

        for i, account in enumerate(accounts, 1):
            # account는 {"123-45-678901": 10000} 같은 구조
            for num, bal in account.items():
                print(f"{i}. {num} | 잔액: {bal}원")
                my_list.append((num, bal, account))

        # 계좌가 하나도 없으면 이체 불가
        if not my_list:
            print("보유한 계좌가 없습니다.")
            return False

        # 돈 보낼 내 계좌번호 입력 받기
        my_acc = input("보낼(출금) 계좌번호 입력: ").strip()

        # 입력받은 내 계좌번호가 실제로 내 계좌 목록에 있는지 확인
        src = None  # (계좌번호, 잔액, 계좌dict)
        for num, bal, acc_dict in my_list:
            if num == my_acc:
                src = (num, bal, acc_dict)
                break
        if not src:
            print("내 계좌번호가 올바르지 않습니다.")
            return False

        # '입금(받을)' 계좌번호 입력 받기
        other_acc = input("받는(입금) 계좌번호 입력: ").strip()

        # 자기 자신에게 이체 방지
        if other_acc == my_acc:
            print("자기 자신에게는 이체할 수 없습니다.")
            return False

        # 전체 사용자(users)에서 '입금 계좌'가 실제 존재하는지 탐색
        recip_user = None  # 수취인 사용자 dict
        recip_dict = None  # 수취인 계좌 dict ({"계좌번호": 잔액})
        for u in db.get("users", []):
            for a in u.get("accounts", []):
                if other_acc in a:
                    recip_user = u
                    recip_dict = a
                    break
            if recip_user:
                break

        # 대상 계좌가 없으면 중단
        if not recip_user:
            print("없는 계좌번호입니다.")
            return False

        # 이체 금액 입력 및 유효성 검사
        try:
            amount = int(input("보낼 금액(원): "))
        except ValueError:
            print("숫자를 입력하세요.")
            return False

        if amount <= 0:
            print("0원 이하는 보낼 수 없습니다.")
            return False

        # 출금 계좌 잔액이 충분한지 확인
        # src = (계좌번호, 잔액, 계좌{account, money}) 이므로, 실제 잔액은 src[2][src[0]]
        if src[2][src[0]] < amount:
            print("잔액이 부족합니다.")
            return False

        # 비밀번호 확인(로그인 비밀번호 기준) — 최대 3회
        for tries in range(3):
            pw = input("이체 비밀번호 확인(로그인 비밀번호 입력): ")
            if pw == password:
                break
            print(f"비밀번호가 올바르지 않습니다. ({tries + 1}/3)")
        else:
            print("비밀번호 입력 3회 오류로 이체가 취소되었습니다.")
            return False

        # 이체 실행
        # 출금 계좌에서 차감
        src[2][src[0]] -= amount
        # 입금 계좌에 가산
        recip_dict[other_acc] += amount

        # 10) 변경된 DB를 파일에 저장하여 영구 반영
        self.storage.save(db)

        print("이체가 완료되었습니다.")
        return True
        """


    # 계좌 입/출금
    def deposit(self):
        if not self._require_login():
            return False
        db = self._sync()

        # id/계좌 호출
        id = self.user.user_id()
        accounts = self.user.user_accounts()

        if not id:
            print("로그인이 필요합니다.")
            return False

        # 계좌 목록 없으면 종료
        if not accounts:
            print("입금할 계좌가 없습니다.")
            return False

        # 계좌 목록은 조회 기능 재사용
        print("\n[계좌 조회]")
        self.search(self.personal)

        # 대상 계좌 선택
        ac_number = input("입금할 계좌번호를 입력하세요: ").strip()
        target_dict = None
        for ac in accounts:
            if ac_number in ac:
                target_dict = ac
                break
        if target_dict is None:
            print("해당 계좌번호를 찾을 수 없습니다.")
            return False

        # 금액 입력 및 검증
        try:
            amount = int(input("입금액(원): "))
        except ValueError:
            print("숫자를 입력하세요.")
            return False
        if amount <= 0:
            print("0원 이하는 입금할 수 없습니다.")
            return False

        # 잔액 반영 및 저장
        target_dict[ac_number] += amount
        self.storage.save(db)
        print(f"{amount}원이 입금되었습니다. 현재 잔액: {target_dict[ac_number]}원")
        return True


    def withdraw(self):
        if not self._require_login():
            return False
        db = self._sync()

        # id/계좌 호출
        id = self.user.user_id()
        accounts = self.user.user_accounts()

        if not id:
            print("로그인이 필요합니다.")
            return False

        # 계좌 목록 없으면 종료
        if not accounts:
            print("출금할 계좌가 없습니다.")
            return False

        # 계좌 목록은 조회 기능 재사용
        print("\n[계좌 조회]")
        self.search(self.personal)

        # 대상 계좌 선택
        ac_number = input("출금할 계좌번호를 입력하세요: ").strip()
        target_dict = None
        for ac in accounts:
            if ac_number in ac:
                target_dict = ac
                break
        if target_dict is None:
            print("해당 계좌번호를 찾을 수 없습니다.")
            return False

        # 금액 입력 및 검증
        try:
            amount = int(input("출금액(원): "))
        except ValueError:
            print("숫자를 입력하세요.")
            return False
        if amount <= 0:
            print("0원 이하는 출금할 수 없습니다.")
            return False
        if target_dict[ac_number] < amount:
            print("잔액이 부족합니다.")
            return False

        # 잔액 반영 및 저장
        target_dict[ac_number] -= amount
        self.storage.save(db)
        print(f"{amount}원이 출금되었습니다. 현재 잔액: {target_dict[ac_number]}원")
        return True

    # 대출 신청
    def loan_request(self):
        if not self._require_login():
            return False
        self._sync()

        id = self.user.user_id()
        name = self.user.user_name()
        accounts = self.user.user_accounts()

        if not id:
            print("사용자 정보를 찾을 수 없습니다.")
            return False

        if not accounts:
            print("대출 신청을 위해서는 계좌가 필요합니다.")
            return False

        # 대출 여부 확인
        user = self.personal.find_user(id)
        loan_info = user.get("loan", {})
        if loan_info.get("amount", 0) > 0:
            print(f"이미 대출이 존재합니다. (잔액: {loan_info['amount']:,}원)")
            return False

        # 계좌 목록 출력
        print(f"\n[{name}]님의 계좌 목록")
        for i, account in enumerate(accounts, 1):
            for account_num, balance in account.items():
                print(f"{i}. 계좌번호: {account_num} | 잔액: {balance:,}원")

        max_loan = 10000000
        account_number = input("대출금을 입금할 계좌번호를 입력하세요: ").strip()

        try:
            amount = int(input(f"대출 신청 금액을 입력하세요 (최대 {max_loan:,}원): ").strip())
        except ValueError:
            print("잘못된 금액 입력입니다.")
            return False

        if amount <= 0 or amount > max_loan:
            print("대출 신청 금액이 한도를 초과했거나 잘못되었습니다.")
            return False

        # 계좌 찾기 및 대출 실행
        for account in accounts:
            if account_number in account:
                account[account_number] += amount  # 대출금 입금
                user["loan"] = {
                    "amount": amount,
                    "date": datetime.now().isoformat(),
                }
                try:
                    self.storage.save(self.personal.db)
                except Exception as e:
                    print("저장 중 오류가 발생했습니다:", e)
                    return False

                print(f"{amount:,}원이 대출되었습니다. 계좌 {account_number}에 입금 완료.")
                return True

        print("해당 계좌번호를 찾을 수 없습니다.")
        return False


    # 대출 조회
    def loan_inquiry(self):
        if not self._require_login():
            return False
        self._sync()

        # id/name/ac 호출
        id = self.user.user_id()
        name = self.user.user_name()
        accounts = self.user.user_accounts()

        if not id:
            print("사용자 정보를 찾을 수 없습니다.")
            return False

        user = self.personal.find_user(id)
        loan_info = user.get("loan")
        if not loan_info or loan_info.get("amount", 0) <= 0:
            print("현재 대출이 없습니다.")
            return False

        amount = loan_info.get("amount", 0)
        date_str = loan_info.get("date")

        loan_date_fmt = None
        if date_str:
            try:
                loan_date_fmt = datetime.fromisoformat(date_str).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                loan_date_fmt = None

        print(f"\n=== 대출 정보 ===")
        print(f"대출 잔액: {loan_info['amount']:,}원")
        if loan_date_fmt:
            print(f"대출 일자: {loan_date_fmt}")
        else:
            print(f"대출 일자: {date_str or '정보 없음'}")
        return True

    # 대출 상환
    def loan_repayment(self):
        if not self._require_login():
            return False
        self._sync()

        id = self.user.user_id()
        name = self.user.user_name()
        accounts = self.user.user_accounts()

        if not id:
            print("사용자 정보를 찾을 수 없습니다.")
            return False

        if not accounts:
            print("상환을 위해서는 계좌가 필요합니다.")
            return False
        # 대출 여부 확인
        user = self.personal.find_user(id)
        loan_info = user.get("loan")
        if not loan_info or loan_info.get("amount", 0) <= 0:
            print("상환할 대출이 없습니다.")
            return False

        loan_amount = int(loan_info.get("amount", 0))
        print(f"\n현재 대출 잔액: {loan_amount:,}원")

        # 계좌 목록 출력
        print(f"\n[{user['name']}]님의 계좌 목록")
        for i, account in enumerate(accounts, 1):
            for account_num, balance in account.items():
                print(f"{i}. 계좌번호: {account_num} | 잔액: {balance:,}원")

        account_number = input("상환할 계좌번호를 입력하세요: ").strip()
        try:
            amount = int(input(f"상환 금액을 입력하세요 (최대 {loan_amount:,}원): ").strip())
        except ValueError:
            print("잘못된 금액 입력입니다.")
            return False

        if amount <= 0:
            print("상환 금액은 0원보다 커야 합니다.")
            return False

        if amount > loan_amount:
            print("상환 금액이 대출 잔액을 초과할 수 없습니다.")
            return False

        # 계좌 찾기 및 상환 실행
        for account in user["accounts"]:
            if account_number in account:
                if account[account_number] < amount:
                    print("계좌 잔액이 부족합니다.")
                    return False

                # 상환 실행
                account[account_number] -= amount  # 계좌에서 출금
                user["loan"]["amount"] -= amount  # 대출 잔액 감소

                # 대출이 완전히 상환되면 대출 정보 삭제
                if loan_info["amount"] == 0:
                    del user["loan"]
                    print(f"{amount:,}원 상환 완료. 대출이 완전히 상환되었습니다!")
                else:
                    print(f"{amount:,}원 상환 완료. 남은 대출 잔액: {loan_info['amount']:,}원")

                try:
                    self.storage.save(self.personal.db)
                except Exception as e:
                    print("저장 중 오류가 발생했습니다:", e)
                    return False
                return True

        print("해당 계좌번호를 찾을 수 없습니다.")
        return False

    def bank_plus(self):
        if not self._require_login():
            return False
        db = self._sync()
        pass
        # 사용할 데이터(id, pw, name, ac 등) 호출
        # id = self.user.user_id()
        # pw = self.user.user_password()
        # name = self.user.user_name()
        # accounts = self.user.user_accounts()

        # 기능 구현