from flask import Flask, render_template, request, session, redirect, url_for
from tinydb import TinyDB, Query
import hashlib
import os
from datetime import datetime

#work on encrypted

app = Flask('app')
app.secret_key = os.urandom(32)
db = TinyDB("data/db.json")
accounts = db.table("accounts")

@app.route('/')
def hellow_world():
  if "username" in session:
    return redirect(url_for("homepage"))
  else:
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    un = request.form['username']
    pw = request.form['password']
    #hash
    encoded = pw.encode()
    hashed_pass = hashlib.sha256(encoded).hexdigest()
    user = Query()
    results = accounts.search(user.username == un)
    if len(results) > 0:
      if results[0]['password'] == hashed_pass:
        session['username'] = un
        return redirect(url_for("homepage"))
      else:
        return render_template("login.html", message="Wrong password.")
    else:
      return render_template("login.html", message="Username not found.")
  else:
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
  if request.method == "POST":
    un = request.form['username_first_time']
    pw = request.form['password_first_time']
    encoded = pw.encode()
    hashed_pass = hashlib.sha256(encoded).hexdigest()
    user = Query()
    results = accounts.search(user.username == un)
    if len(results) > 0:
      return render_template("signup.html", message="Username already taken.")
    else:
      accounts.insert({"username": un, "password": hashed_pass, "messages": [], "current_id": 0 })
      return render_template("login.html", message="Account created. Please login.")
  else:
    return render_template("signup.html")

@app.route("/home")
def homepage():
  if "username" in session:
    #grab their messages
    user = Query()
    results = accounts.search(user.username == session['username'])
    messages = results[0]['messages']
    if "message" in session:
      temp = session['message']
      del session['message']
      return render_template("homepage.html", message = temp, messages = messages)
    else:
      return render_template("homepage.html", messages = messages)
  else:
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
  if session["username"]:
    del session['username']
  return redirect(url_for("login"))

@app.route("/new", methods=["GET", "POST"])
def newMessage():
  if "username" in session:
    if request.method == "POST":
      recipient = request.form['recipient']
      subject = request.form['subject']
      message = request.form['message']
      read = False
      encrypted = request.form.get("encrypted")
      password = request.form['password']

      encoded = password.encode('utf-8')
      hashed_pass = hashlib.sha256(encoded).hexdigest()

      now = datetime.now()
      hr = int(now.strftime("%I")) - 4
      tm = str(hr) + now.strftime(":%M %p")
      dt = now.strftime("%m/%d/%Y")

      user = Query()
      results = accounts.search(user.username == recipient)

      if len(results) > 0:
        messages = results[0]['messages']
        current_id = results[0]['current_id']

        messages.append({"id": current_id, "sender": session['username'], "subject": subject, "message": message, "date": dt, "time": tm, "read": read, "encrypted": encrypted, "password": hashed_pass })
        accounts.update({"messages": messages, "current_id": current_id + 1}, user.username == recipient)
        
        session['message'] = "Message sent."
      else:
        session['message'] = "User doesn't exist."
      return redirect(url_for("homepage"))
    else:
      return render_template("new.html")
  else:
    return redirect(url_for("login"))

@app.route("/message/<id>")
def getMessage(id):
  user = Query()
  results = accounts.search(user.username == session['username'])
  messages = results[0]['messages']
  for x in messages:
    if x['id'] == int(id):
      if x['encrypted']:
        return messagePassword(id)
      else:
        x['read'] = True
        accounts.update({"messages": messages}, user.username == session['username'])
        return render_template("message.html", message = x)
  session['message'] = "Message not found."
  return redirect(url_for("homepage"))

@app.route("/messagelock/<id>", methods=['GET', "POST"])
def messagePassword(id):
  if "username" in session:
    if request.method != "POST":
      return render_template("messagelockig.html", id = id)
    else:
      user = Query()
      results = accounts.search(user.username == session['username'])
      messages = results[0]['messages']
      current_message = {}

      for message in messages:
        if message['id'] == int(id):
          message['read'] = True
          accounts.upsert({"messages": messages}, user.username == session['username'])
          current_message = message
          break
      
      password = current_message['password']
      input_password = request.form['password']

      encoded = input_password.encode('utf-8')
      hashed_pass = hashlib.sha256(encoded).hexdigest()

      if hashed_pass == password:
        return render_template("message.html", message = current_message)
      else:
        return render_template("messagelockig.html", message = "Wrong password.", id = id)

  else:
    return "Not logged in."

app.debug = True
app.run(host='0.0.0.0', port=8080)