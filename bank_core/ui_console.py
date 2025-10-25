
# ui_console.py - 콘솔 UI
# 이 파일은 사용자와 상호작용하는 콘솔 기반 인터페이스를 제공합니다.
# 메뉴 출력, 입력 처리, 서비스 계층 호출 등만 담당합니다.

from bank_core.storage import BankStorage
from bank_core.service import BankService


def main():
    """
    프로그램의 메인 진입점
    - 회원가입, 로그인, 종료 메뉴 제공
    """
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
            print("잘못된 입력입니다. 다시 입력하세요.")


def user_menu(service):
    """
    로그인 후 사용자 메뉴
    - 계좌 조회, 생성, 입금, 출금, 이체, 로그아웃 등 제공
    """
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
            # 계좌 목록 출력
            for acc in service.current_user.accounts:
                print(acc)

        elif choice == "2":
            # 신규 계좌 생성
            ok, msg = service.create_account()
            print(msg)

        elif choice == "3":
            # 입금 처리
            acc_num = input("입금할 계좌번호: ").strip()
            try:
                amt = int(input("입금액: "))
            except ValueError:
                print("입금액은 숫자로 입력하세요.")
                continue
            ok, msg = service.deposit(acc_num, amt)
            print(msg)

        elif choice == "4":
            # 출금 처리
            acc_num = input("출금할 계좌번호: ").strip()
            try:
                amt = int(input("출금액: "))
            except ValueError:
                print("출금액은 숫자로 입력하세요.")
                continue
            ok, msg = service.withdraw(acc_num, amt)
            print(msg)

        elif choice == "5":
            # 계좌이체 처리
            ok, msg = service.transfer()
            print(msg)

        elif choice == "6":
            # 로그아웃 및 계좌 상태 출력
            print("로그아웃 되었습니다. 현재 계좌 상태:")
            for acc in service.current_user.accounts:
                print(acc)
            service.logout()
            break

        else:
            print("잘못된 입력입니다. 다시 입력하세요.")


if __name__ == "__main__":
    main()
