import sys


# 다른 클래스들을 호출하는 클래스
class Main:
    def __init__(self, per, acc):
        self.per = per
        self.acc = acc

    def login_main(self, choice : str) -> bool:
        if choice == "0":
            self.per.join()
            return True
        elif choice == "1":
            self.per.login()
            return True
        elif choice == "9":
            print("종료합니다.")
            sys.exit(0)
        else:
            print("올바른 번호를 입력하세요.")
            return True

    def logout_main(self, choice):
        if choice == "0":
            self.per.join()
            return True
        elif choice == "1":
            self.per.logout()
            return True
        elif choice == "9":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("올바른 번호를 입력하세요.")
            return True

    def account_main(self, choice):
        if choice == "0":
            self.acc.search(self.per)
            return True
        elif choice == "1":
            self.acc.new_account(self.per)
            return True
        elif choice == "2":
            self.acc.delete_account(self.per)
            return True
        elif choice == "3":
            self.acc.transfer_account(self.per)
            return True
        elif choice == "8":
            return False
        elif choice == "9":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("올바른 번호를 입력하세요.")
            return True

    def deposit_withdraw_main(self, choice):
        if choice == "0":
            self.acc.deposit()
            return True
        elif choice == "1":
            self.acc.withdraw()
            return True
        elif choice == "8":
            return False
        elif choice == "9":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("올바른 번호를 입력하세요.")
            return True

    def loan_main(self, choice):
        if choice == "0":
            self.acc.loan_request()
            return True
        elif choice == "1":
            self.acc.loan_inquiry()
            return True
        elif choice == "2":
            self.acc.loan_repayment()
            return True
        elif choice == "8":
            return False
        elif choice == "9":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("올바른 번호를 입력하세요.")
            return True