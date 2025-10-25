# 이체를 위한 필요요소
# 상대방 계좌 조회(계좌 번호, 이름)
# 나의 계좌 정보(계좌 번호, 이름, 계좌 잔액, 비밀번호)
# 상대방


src_name = "다니엘"
src_account = "123-1234-1234"
Recipient_account = ""
Recipient_name = ""
save_money = 3000
Send_name = "다니엘"
password = "123456"

def check_password():
    i_password =  input("이체를 완료 할려면 패스워드를 입력해 주세요.")
    if i_password != password:
        print("패스워드가 맞지 않습니다. 다시 입력해주세요.")
    else:
        print("이체가 성공적으로 이뤄졌습니다. 감사합니다.")

def message():
    global Send_name
    print(f"상대방 통장에 표시 되는 이름을 변경 하실 수 있습니다.  \n 현재이름 : {Send_name}")
    while True:
        change = int(input("변경하고 싶으면 1번을, 그대로 보내시거면 2번을 눌러주세요 : "))
        if change == 1:
            Send_name = input("변경 할 내용을 입력해주세요. : ")
            check_password()
            break
        elif change == 2:
            check_password()
            break
        else:
            print("잘못 입력하셨습니다.")
            continue

def how_much():
    print(f"입력하신 계좌와 이름은 다음과 같습니다.\n 받는분 계좌번호 : {Recipient_account} \n 받는분 : {Recipient_name}")
    while True:
        send_money = int(input("이체 하실 금액을 입력해 주세요.(숫자만) : "))
        if save_money < send_money:
            print(f"보낼 수 있는 금액을 확인하고 다시 입력해 주세요 : {save_money}")
            continue
        else:
            message()
            break

def check_name():
    global Recipient_name
    while True:
        name = input("이체 하실 받는 분 이름을 넣어주세요 : ")
        if name != src_name:
            print("받는 분의 이름이 맞지 않습니다. 다시 확인 해 주세요.")
            continue
        else:
            Recipient_name = name
            how_much()
            break

def check_account() :
    global Recipient_account
    while True:
        account = input("이체 하실 계좌번호를 입력해 주세요 : ")
        # 입력값으로 json 리스트에서 찾는다.
        if account != src_account:
            print("없는 계좌번호 입니다. 다시 확인 해 주세요.")
            continue
        else:
            Recipient_account = account
            check_name()
            break



if __name__ == "__main__":
    check_account()