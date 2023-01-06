################################################################################
#Chrome forensics tool
#Developed by Boris Ivanov
################################################################################
import os
from os import path
import sqlite3
import datetime
from datetime import date
import pandas as pd
import humanTime

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

today = date.today()
#Chrome default folder
print("[+]Hint! Usually(C:\\Users\\username\AppData\Local\Google\Chrome\\User Data\Default)")
root_dir = input("[+]Enter Chrome's default folder path: ")

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



saveFile = ("data/" + today.strftime("%b-%d-%Y") + ".xlsx")
with pd.ExcelWriter(saveFile) as writer:
    df_url.to_excel(writer, sheet_name="History", index=False)
    df_login.to_excel(writer, sheet_name="LoginData", index=False)
    df_predict.to_excel(writer, sheet_name="Action Predictor", index=False)
    df_phone.to_excel(writer, sheet_name="Phone numbers", index=False)
    df_card.to_excel(writer, sheet_name="Credit cards", index=False)
print("\n[+]XLSX Report created succesfully")
