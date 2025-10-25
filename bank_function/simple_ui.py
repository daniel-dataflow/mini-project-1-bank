# 새 UI: 서비스 계층만 호출하는 간단한 콘솔 인터페이스
from bank_function.bank_storage import BankStorage
from bank_function.services import BankService

def main():
    storage = BankStorage("bank.json")
    service = BankService(storage)

    while True:
        print("\n===== 세종은행 메인 메뉴 =====")
        print("1. 회원가입")
        print("2. 로그인")
        print("3. 종료")
        choice = input("번호를 입력하세요: ").strip()
        if choice == "1":
            name = input("이름: ").strip()
            user_id = input("ID: ").strip()
            pw = input("PW: ").strip()
            ok, msg = service.join(name, user_id, pw)
            print(msg)
        elif choice == "2":
            user_id = input("ID: ").strip()
            pw = input("PW: ").strip()
            ok, msg = service.login(user_id, pw)
            print(msg)
            if ok:
                user_menu(service)
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")

def user_menu(service):
    while True:
        print(f"\n[{service.current_user.name}]님 환영합니다!")
        print("1. 계좌목록 조회")
        print("2. 신규계좌 생성")
        print("3. 입금")
        print("4. 출금")
        print("5. 계좌이체")
        print("6. 로그아웃")
        choice = input("번호를 입력하세요: ").strip()
        if choice == "1":
            for acc in service.current_user.accounts:
                print(acc)
        elif choice == "2":
            ok, msg = service.create_account()
            print(msg)
        elif choice == "3":
            acc_num = input("입금할 계좌번호: ").strip()
            amt = int(input("입금액: "))
            ok, msg = service.deposit(acc_num, amt)
            print(msg)
        elif choice == "4":
            acc_num = input("출금할 계좌번호: ").strip()
            amt = int(input("출금액: "))
            ok, msg = service.withdraw(acc_num, amt)
            print(msg)
        elif choice == "5":
            # 첨부파일의 상세 이체 프로세스 호출
            ok, msg = service.transfer()
            print(msg)
        elif choice == "6":
            service.logout()
            print("로그아웃 되었습니다.")
            break
        else:
            print("잘못된 입력입니다.")

if __name__ == "__main__":
    main()
