import re
import sqlite3
from datetime import datetime as ss

# إنشاء الاتصال بقاعدة البيانات
db = sqlite3.connect("ZEQ.db")
sr = db.cursor()

# إنشاء الجدول مع تعيين id كـ Primary Key لمنع التكرار
sr.execute(
    """CREATE TABLE IF NOT EXISTS Users (
        id TEXT PRIMARY KEY,
        name TEXT,
        phone_Number TEXT,
        email TEXT,
        balance REAL
    )"""
)
db.commit()

# متغيرات حالة التطبيق
Transaction = []
Total_Deposit = 0.0
Total_Withdraw = 0.0

data = """
=============================
   BANK MANAGEMENT SYSTEM
=============================
"1" =>> Add New Account
"2" =>> Show All Account
"3" =>> Search Account
"4" =>> Update Account
"5" =>> Delete Account
"6" =>> Deposit
"7" =>> Withdraw
"8" =>> Transfer Money
"9" =>> Transaction History
"10" =>> Bank Statistics
"11" =>> Exit
=============================
Enter Your Choice: """


# =====================================METHODS=====================================================
def Add_Account():
    Id = input("Enter Account ID: ").strip()
    if not Id:
        print("ID cannot be empty.")
        return

    # استخدام Parameterized Queries للوقاية من حقن SQL
    sr.execute("SELECT id FROM Users WHERE id=?", (Id,))
    if sr.fetchone() is not None:
        print("ID exists, try another ID.")
        return

    name = input("Enter Customer Name: ").strip()
    if not name:
        print("Name is invalid.")
        return

    number = input("Enter Phone Number: ").strip()
    # التحقق من أن رقم الهاتف يتكون من 10 أرقام ويبدأ بـ 05
    if not re.fullmatch(r"05[0-9]{8}", number):
        print("Number is invalid (Must be 10 digits starting with 05).")
        return

    email = input("Enter Email: ").strip()
    # التحقق الصحيح من صيغة البريد الإلكتروني
    if not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        print("Email format is invalid.")
        return

    try:
        initial_balance = float(input("Enter Initial Balance: "))
        if initial_balance < 0:
            print("Initial Balance must be non-negative.")
            return
    except ValueError:
        print("Invalid balance input! Please enter a valid number.")
        return

    sr.execute(
        "INSERT INTO Users (id, name, phone_Number, email, balance) VALUES (?, ?, ?, ?, ?)",
        (Id, name, number, email, initial_balance),
    )
    db.commit()
    print("Account Created Successfully!")


# ==============================================================================================
def Show_All_Account():
    sr.execute("SELECT name, id, balance FROM Users")
    result = sr.fetchall()
    if result:
        print(f"\nUsers Have {len(result)} Account(s)")
        print("Account:")
        print("=" * 20)
        for x in result:
            print(f"Name: {x[0]}")
            print(f"ID: {x[1]}")
            print(f"Balance: {x[2]}$")
            print("*" * 20)
    else:
        print("No Account Found")


# =========================================================================================
def Sarech_Account():
    input_id = input("Enter ID: ").strip()
    sr.execute(
        "SELECT id, name, phone_Number, email, balance FROM Users WHERE id=?",
        (input_id,),
    )
    row = sr.fetchone()
    if row:
        print("\nAccount Details:")
        print(f"Account ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Phone Number: {row[2]}")
        print(f"Email: {row[3]}")
        print(f"Balance: {row[4]}$")
        print("*" * 20)
    else:
        print("Account Not Found")


# =============================================================================================
def Update_Account():
    input_id = input("Enter ID: ").strip()
    sr.execute("SELECT id FROM Users WHERE id=?", (input_id,))
    if not sr.fetchone():
        print("Account Not Found.")
        return

    change = """
 "1" =>> Change Name
 "2" =>> Change Phone
 "3" =>> Change Email
 Enter Choice: """
    Input_choices = input(change).strip()

    if Input_choices == "1":
        New_Name = input("Enter New Name: ").strip()
        if New_Name:
            sr.execute(
                "UPDATE Users SET name=? WHERE id=?", (New_Name, input_id)
            )
            db.commit()
            print("Name Updated Successfully")
        else:
            print("Name cannot be empty.")
    elif Input_choices == "2":
        New_Num = input("Enter New Phone Number: ").strip()
        if re.fullmatch(r"05[0-9]{8}", New_Num):
            sr.execute(
                "UPDATE Users SET phone_Number=? WHERE id=?", (New_Num, input_id)
            )
            db.commit()
            print("Phone Number Updated Successfully")
        else:
            print("Invalid Phone Number.")
    elif Input_choices == "3":
        New_Email = input("Enter New Email: ").strip()
        if re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", New_Email
        ):
            sr.execute(
                "UPDATE Users SET email=? WHERE id=?", (New_Email, input_id)
            )
            db.commit()
            print("Email Updated Successfully")
        else:
            print("Invalid Email.")
    else:
        print("Error choice")


# ===========================================================================================
def Delete_Account():
    input_id = input("Enter ID: ").strip()
    sr.execute("SELECT id FROM Users WHERE id=?", (input_id,))
    if not sr.fetchone():
        print("Account Not Found.")
        return

    ss_choice = (
        input("Are You Sure You Want To Delete This Account? Yes/No : ")
        .strip()
        .capitalize()
    )
    if ss_choice in ["Yes", "Y"]:
        sr.execute("DELETE FROM Users WHERE id=?", (input_id,))
        db.commit()
        print("Delete Successfully")
    else:
        print("Delete Not Successfully")


# ===================================================================================
def Deposit():
    global Total_Deposit
    id_input = input("Enter Account ID: ").strip()

    sr.execute("SELECT balance FROM Users WHERE id=?", (id_input,))
    result = sr.fetchone()
    if not result:
        print("Account Not Found.")
        return

    try:
        amount = float(input("Enter Amount: "))
        if amount > 0:
            sr.execute(
                "UPDATE Users SET balance = balance + ? WHERE id=?",
                (amount, id_input),
            )
            db.commit()

            sr.execute("SELECT balance FROM Users WHERE id=?", (id_input,))
            res = sr.fetchone()
            print("Deposit Successfully")
            print(f"New Balance is:{res[0]}$")

            Deposit_dict = {
                "Type": "Deposit",
                "Account_id": id_input,
                "Amount": amount,
                "Date": ss.now().strftime("%Y/%m/%d - %H:%M:%S"),
            }
            Transaction.append(Deposit_dict)
            Total_Deposit += amount
        else:
            print("Deposit Must be greater than Zero")
    except ValueError:
        print("Invalid amount! \n Please enter a valid number.")


# ============================================================================================
def Withdraw():
    global Total_Withdraw
    id_input = input("Enter Account ID: ").strip()

    sr.execute("SELECT balance FROM Users WHERE id=?", (id_input,))
    result = sr.fetchone()
    if not result:
        print("Account Not Found.")
        return

    current_balance = result[0]
    try:
        amount = float(input("Enter Amount: "))
        if amount <= 0:
            print("Amount Must be greater than Zero")
        elif amount <= current_balance:
            sr.execute(
                "UPDATE Users SET balance = balance - ? WHERE id=?",
                (amount, id_input),
            )
            db.commit()

            sr.execute("SELECT balance FROM Users WHERE id=?", (id_input,))
            x = sr.fetchone()
            print("Withdraw Successfully")
            print(f"New Balance is:{x[0]}$")

            Withdraw_dict = {
                "Type": "Withdraw",
                "Account_id": id_input,
                "Amount": amount,
                "Date": ss.now().strftime("%Y/%m/%d - %H:%M:%S"),
            }
            Transaction.append(Withdraw_dict)
            Total_Withdraw += amount
        else:
            print("Insufficient balance")
    except ValueError:
        print("Invalid amount! \n Please enter a valid number.")


# ======================================================================================
def Transfer():
    sender_id = input("Enter Sender Account ID: ").strip()
    receiver_id = input("Enter Receiver Account ID: ").strip()

    if sender_id == receiver_id:
        print("Sender Account = Receiver Account")
        return

    sr.execute("SELECT balance FROM Users WHERE id=?", (sender_id,))
    sender_res = sr.fetchone()

    sr.execute("SELECT id FROM Users WHERE id=?", (receiver_id,))
    receiver_res = sr.fetchone()

    if not sender_res:
        print("Sender Account Not Found")
        return
    if not receiver_res:
        print("Receiver Account Not Found")
        return

    sender_balance = sender_res[0]

    try:
        amount = float(input("Enter Amount: "))
        if amount <= 0:
            print("Amount must be greater than Zero")
            return
        if sender_balance < amount:
            print("Insufficient balance")
            return

        # تنفيذ عملية التحويل لـ الحسابين معاً
        sr.execute(
            "UPDATE Users SET balance = balance - ? WHERE id=?",
            (amount, sender_id),
        )
        sr.execute(
            "UPDATE Users SET balance = balance + ? WHERE id=?",
            (amount, receiver_id),
        )
        db.commit()

        print("Transfer is Successfully")

        sr.execute("SELECT balance FROM Users WHERE id=?", (sender_id,))
        x = sr.fetchone()
        sr.execute("SELECT balance FROM Users WHERE id=?", (receiver_id,))
        y = sr.fetchone()

        print(f"Sender New Balance is : {x[0]}$")
        print(f"Receiver New Balance is : {y[0]}$")

        Transfer_dict = {
            "Type": "Transfer",
            "From": sender_id,
            "To": receiver_id,
            "Amount": amount,
            "Date": ss.now().strftime("%Y/%m/%d - %H:%M:%S"),
        }
        Transaction.append(Transfer_dict)
    except ValueError:
        print("Invalid amount! \n Please enter a valid number.")


# ======================================================================
def Transaction_History():
    print("=" * 20)
    print("Transaction_History")
    print("=" * 20)
    if len(Transaction) > 0:
        for c in Transaction:
            print(c)
            print("======================")
    else:
        print("No Transaction")


# ==================================================================
def Bank_Statistics():
    sr.execute("SELECT balance FROM Users")
    result = sr.fetchall()
    if len(result) > 0:
        all_Balance = [row[0] for row in result]
        total_acc = len(all_Balance)
        net_money = Total_Deposit - Total_Withdraw
        max_balance = max(all_Balance)
        min_balance = min(all_Balance)
        avg_balance = sum(all_Balance) / total_acc

        print("\nBank Statistics")
        print("*" * 20)
        print(f"Total Account is : {total_acc}")
        print(f"Total Deposit is : {Total_Deposit}$")
        print(f"Total Withdraw is : {Total_Withdraw}$")
        print(f"Net Money Movement is : {net_money}$")
        print(f"Max Balance is :{max_balance}$")
        print(f"Min Balance is :{min_balance}$")
        print(f"Average Balance is :{avg_balance:.2f}$")
        print("*" * 20)
    else:
        print("No Data Found")


def Exit():
    print("Thank You For Using Our Bank System! \n Good Bye!")
    db.close()


# ======================================================================
# الحلقة الرئيسية لتشغيل القائمة
while True:
    Input = input(data).strip()
    if Input == "1":
        Add_Account()
    elif Input == "2":
        Show_All_Account()
    elif Input == "3":
        Sarech_Account()
    elif Input == "4":
        Update_Account()
    elif Input == "5":
        Delete_Account()
    elif Input == "6":
        Deposit()
    elif Input == "7":
        Withdraw()
    elif Input == "8":
        Transfer()
    elif Input == "9":
        Transaction_History()
    elif Input == "10":
        Bank_Statistics()
    elif Input == "11":
        Exit()
        break
    else:
        print("Invalid Choice, Please Try Again")
