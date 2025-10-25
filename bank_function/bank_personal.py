from datetime import datetime
import random

# 회원가입/로그인 시스템 구현 클래스
class BankPersonal:
    def __init__(self, storage):
        self.storage = storage
        self.db = self.storage.load()
        self.current_login = 0
        self.current_user_id = None


    # id가 있으면 해당 dict를 반환, 아니면 None 반환
    def find_user(self, user_id) -> dict | None:
        for u in self.db["users"]:
            if u["id"] == user_id:
                return u
        return None

    # 계좌 중복 확인
    def account_exists(self, ac) -> bool:
        for user in self.db["users"]:
            for account in user.get("accounts", []):
                if ac in account:  # dict의 키 검사
                    return True
        return False

    # 회원가입 기능
    def join(self) -> bool:
        name = input("가입할 이름을 입력하세요: ").strip()
        user_id = input("가입할 ID를 입력하세요: ").strip()

        # 가입할 id가 이미 있으면)
        if self.find_user(user_id):
            print("이미 존재하는 ID입니다.")
            return False

        # id/pw 입력
        pw = input("가입할 PW를 입력하세요: ").strip()

        # 랜덤 계좌번호 생성 ("0000-00-0000")
        ac_list = list()
        ac_list.append('{0:04d}'.format(random.randint(0, 9999)))
        ac_list.append('{0:02d}'.format(random.randint(0, 99)))
        ac_list.append('{0:04d}'.format(random.randint(0, 9999)))


        ac = '-'.join(map(str, ac_list))

        # 같은 계좌가 이미 있으면 안댐
        if self.account_exists(ac):
            print("이미 존재하는 계좌번호입니다.")
            return False

        self.db["users"].append({
            "name": name,
            "id": user_id,
            "password": pw,  # 학습용: 평문 저장
            "accounts": [{ac : 0}], # 계좌번호 : 잔액
            "opening_date" : datetime.now().isoformat()
        })

        self.storage.save(self.db)
        print("가입완료!")
        print(f"계좌번호 : {ac}\n")
        return True

    # 로그인 기능
    def login(self) -> bool:
        user_id = input("아이디를 입력하세요: ")
        pw = input("패스워드를 입력하세요: ")

        user = self.find_user(user_id)
        # ID 있는지/맞았는지 확인!
        if not user:
            print("가입된 ID가 없거나 ID가 틀렸습니다. 다시 시도해주세요.\n")
            return False

        # PW 있는지/맞았는지 확인!
        if user["password"] != pw:
            print("비밀번호가 틀렸습니다. 다시 시도해주세요.\n")
            return False

        # current_login에 1 반환 (로그인된 상태)
        self.current_login = 1
        # user값 저장 (해당 값을 기준으로 출력)
        self.current_user_id = user_id
        print(f"로그인 성공! {user['name']} 님 환영합니다!\n")
        return True

    # 로그아웃 기능
    def logout(self):
        if self.current_login:
            print("로그아웃 되었습니다!\n")
        # current_login에 0 반환 (로그아웃된 상태)
        self.current_login = 0
        self.current_user_id = None
        return True
