from tinydb import TinyDB, Query
from datetime import datetime
from cryptography.fernet import Fernet

'''
db = TinyDB("test_db.json")
accounts = db.table("accounts")

print("adding user bob...")
accounts.insert({"username": "bob", "password": "bob2", "messages": [], "current_id": 0 })

print("adding user john...")
accounts.insert({"username": "john", "password": "john2", "messages": [], "current_id": 0 })

print("bob will send a message to john")
#search 4 john
recipient = "john"
subject = "important info inside"
message = " hello hope u have a nice day xd"

user = Query()
results = accounts.search(user.username == "john")

#if they exist
if len(results) > 0:
  messages = results[0]['messages']
  current_id = results[0]['current_id']

  messages.append({"id": current_id, "recipient": recipient, "subject": subject, "message": message })
  accounts.update({"messages": messages, "current_id": current_id + 1}, user.username == "john")
else:
  print("no exist")

now = datetime.now()
print(now)
hr = int(now.strftime("%I")) - 4
tm = str(hr) + now.strftime(":%M %p")

dt = now.strftime("%m/%d/%Y")
print(tm)
print(dt)
'''

def generate_key():
  key = Fernet.generate_key()
  with open("data/secret.key", "wb") as key_file:
      key_file.write(key)