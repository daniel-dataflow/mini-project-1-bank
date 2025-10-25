
from bank_transfer_services import BankService
from bank_storage import BankStorage

if __name__ == "__main__":
    # 1. 데이터 저장 Storage
    main_db_storage = BankStorage(path="bank.json")
    log_db_storage = BankStorage(path="transaction_log.json")

    # 2. Bank_Service
    bank_service = BankService(
        bank_storage=main_db_storage,
        log_storage=log_db_storage
    )

    # 3. 서비스를 실행합니다.
    bank_service.run()

    print("\n====== 최종 계좌 상태 확인 ======")
    for user in bank_service.users.values():
        print(f"[{user.name}님의 계좌 목록]")
        # 각 User가 가지고 있는 모든 Account 객체를 순회합니다.
        for account in user.accounts:
            # __str__ 메서드 사용
            print(f"-> {account}")
    print("===============================")