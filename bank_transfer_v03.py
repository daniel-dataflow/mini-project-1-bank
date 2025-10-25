import json

"""
 이체를 위한 필요요소
1. 나의 계좌 정보(계좌 번호, 이름, 계좌 잔액, 비밀번호)
2. 상대방 계좌 조회(계좌 번호, 이름)
3. 보낼 금액 입력
4. 비밀번호 확인
5. 최종 확인
"""
with open("../bank.json", "r", encoding="utf-8") as file:
    bank = json.load(file)
# print(bank)

my_account = list(bank['users'][0]["accounts"][0].keys())[0]
my_balance = list(bank['users'][0]["accounts"][0].values())[0]
my_password = bank['users'][0].get("password")
my_name = bank['users'][0].get("name")

"""
{'users': 
     [{'name': '안호용', 'id': 'hodol0213', 'password': '010213!', 'accounts': [{'943202-00-912073': 0}]}, 
      {'name': 'asdf', 'id': '123', 'password': '123', 'accounts': [{'123': 0}]}]}
"""

# 내 계좌 정보 (로그인 되었다고 가정)
# my_account = accounts_db[0]
# 받는 사람의 정보
recipient = {}

#계좌 데이터베이스에서 계좌번호로 계좌 정보를 찾아 반환
def find_account(account_number):

    for user_info in bank['users']: # 은행에서 유저 항목 돌리기

        account_data = user_info["accounts"] # 유저별 정보
        for account_dict in user_info["accounts"]: #유저에 있는 계좌 가져오기

            if account_number in account_dict : #유저가 가지고 있는 계좌 안에 일치하는지 확인
                recipient["account"] = account_number # 받는사람 계좌번호 넣기
                recipient["name"] = user_info.get("name") # 받는사람 이름 넣기
                recipient["balance"] = account_dict.get(account_number) # 받는사람 잔액 넣기

                return recipient
    return None  # 계좌를 찾지 못하면 None을 반환

#이체할 상대방의 계좌번호와 이름을 입력받아 해당 계좌 정보를 반환
def get_recipient_info():

    while True:
        account_number = input("이체하실 계좌번호를 입력해 주세요: ")

        # 자기 자신에게 이체하는 경우 방지
        if account_number == my_account:
            print("자기 자신에게는 이체할 수 없습니다.")
            continue

        recipient = find_account(account_number)
        if not recipient:  # recipient가 None 이면
            print("없는 계좌번호 입니다. 다시 확인해 주세요.")
            continue

        check_name = input(f"받는 분 : {recipient["name"]}이 맞으신가요? (y/n): ").lower()
        if check_name != 'y':
            print("받는 분의 이름이 맞지 않습니다. 다시 확인해 주세요.")
            get_recipient_info()

        return recipient

#이체할 금액을 입력받아 반환
def get_transfer_amount():

    print(f"현재 나의 잔액: {my_balance}원")
    while True:
        try:
            amount = int(input("이체하실 금액을 입력해 주세요 (숫자만): "))
            if amount <= 0:
                print("0원 이하의 금액은 보낼 수 없습니다.")
                continue
            if my_balance < amount:
                print(f"잔액이 부족합니다. 보낼 수 있는 최대 금액: {my_balance}원")
                continue

            return amount
        except ValueError:
            print("숫자만 입력해주세요.")

# bank Data의 업데이트
def update_balance_in_bank(account_number, amount):
    for user in bank['users']:
        for account_dict in user['accounts']:
            if account_number in account_dict:    # 계좌 딕셔너리에 우리가 찾는 계좌번호가 있는지 확인
                account_dict[account_number] += amount # 잔액을 amount만큼 변경
                return True # 성공적으로 업데이트했음을 알림
    # 모든 계좌를 다 찾아봤는데도 없으면 실패를 알림
    return False

# 이체 최종 확인 및 비밀번호를 검증
def confirm_transfer(recipient, amount):
    global my_balance
    print("\n------ 이체 정보 확인 ------")
    print(f"받는 분: {recipient["name"]}")
    print(f"받는 분 계좌번호: {recipient["account"]}")
    print(f"보내는 금액: {amount}원")
    print("----------------------------")

    # 보내는 사람 이름 변경 기능 (선택적)
    sender_display_name = my_name
    change_name_choice = input(f"받는 분 통장에 표시될 이름을 변경하시겠습니까? (현재: {sender_display_name}) (y/N): ").lower()
    if change_name_choice == 'y':
        sender_display_name = input("변경할 이름을 입력해주세요: ")

    # 비밀번호 확인
    for i in range(3):  # 3번의 기회
        password = input("계좌 비밀번호를 입력해주세요: ")
        if password == my_password:

            # 실제 이체 로직 (잔액 변경)

            receiver_updated = update_balance_in_bank(recipient["account"], amount)
            sender_updated = update_balance_in_bank(my_account, -amount)
            if receiver_updated and sender_updated:
                with open("../bank.json", "w", encoding="utf-8") as file:
                    json.dump(bank, file, ensure_ascii=False, indent=4)
                my_balance -= amount
                # recipient["balance"] += amount
                print("\n✅ 이체가 성공적으로 완료되었습니다.")
                print(f"보내는 분: {sender_display_name}")
                print(f"남은 잔액: {my_balance}원")
                # print(recipient)
                return True  # 성공
            else:
                print("\n❌ 오류: 계좌 정보를 업데이트하는 데 실패했습니다. 이체가 취소됩니다.")
                return False
        else:
            n = 2
            n -= i
            print(f"비밀번호가 틀렸습니다. 다시 시도해주세요.(남은 기회 {n}번)")

    print("❌ 비밀번호를 3회 이상 틀려 이체를 취소합니다.")
    return False  # 실패


def main():

    print("====== 세종 은행 이체 서비스 ======")
    print(f"안녕하세요, {my_name}님!")
    print(f"현재 잔액: {my_balance}원")
    print("==============================")

    # 1. 받는 사람 정보 입력
    recipient_account = get_recipient_info()
    if not recipient_account:
        return  # 이체 취소

    # 2. 보낼 금액 입력
    transfer_amount = get_transfer_amount()

    # 3. 이체 최종 확인
    confirm_transfer(recipient_account, transfer_amount)

    print("\n====== 현재 계좌 정보 ======")
    print(f" {my_name}님 계좌")
    print(f"현재 잔액: {my_balance}원")
    print("==============================")
    # print(bank)


if __name__ == "__main__":
    main()