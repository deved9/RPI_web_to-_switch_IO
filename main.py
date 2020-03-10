from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt
from itertools import count
import sys, sqlite3, random, socket

app = Flask(__name__)
app.config["SECRET_KEY"] = random.randint(100,10000)
bcrypt = Bcrypt(app)
dbconn = sqlite3.connect("user.db")
dbc = dbconn.cursor()
dbc.execute("CREATE TABLE IF NOT EXISTS Users (jmeno,prijmeni,username,password)")
nazvy_tlacitek = ["1","2","3","4","5","6","7","8"]
piny = []
ip = []

with open("piny.private","r") as fin:
   p = list(map(int,fin.read().split()))
   for key,status in enumerate(p):
      piny.append([key+1,status])
   

@app.route("/")
def index():
   if not request.remote_addr in ip:
      return redirect(url_for("login"))
   result = []
   for nazev,p in zip(nazvy_tlacitek,piny):
      result.append([nazev,p[1]])
   return render_template("index.html", result= result)

@app.route("/api_set",methods=["POST","GET"])
def get_req():
   if request.method == "GET":
      return redirect(url_for("login"))
   else:
      pin = int(request.form["pin"])
      piny[pin-1][1] = (piny[pin-1][1]+1)%2
      with open("piny.private","w") as fout:
         for p in piny: 
            fout.write(str(p[1]))
            fout.write(" ")
      return render_template("login.html")

@app.route("/api_reg",methods=["POST","GET"])
def api_reg():
   if request.method == "POST":
      if request.form["pass"] == "":
         return redirect(url_for("login"))
      conn = sqlite3.connect("user.db")
      c = conn.cursor()
      c.execute("SELECT * FROM Users WHERE username = (?)",(request.form["username"],))
      if c.fetchall() == []:
         c.execute("INSERT INTO Users VALUES (?,?,?,?)",(request.form["name"],request.form["surename"],request.form["username"],bcrypt.generate_password_hash(request.form["pass"])))
         conn.commit()
      return redirect(url_for("login"))
   else:
      return redirect(url_for("login"))

@app.route("/api_login",methods=["POST","GET"])
def api_login():
   if request.method == "GET":
      return redirect(url_for("login"))
   if request.form["pass"] == "":
      return redirect(url_for("login"))
   conn = sqlite3.connect("user.db")
   c = conn.cursor()
   c.execute("SELECT password FROM Users WHERE username = (?)",(request.form["username"],))
   hash_pass = c.fetchone()
   if not hash_pass:
      return redirect(url_for("login"))
   hash_pass = hash_pass[0]
   if bcrypt.check_password_hash(hash_pass,request.form["pass"]):
      ip.append(request.remote_addr)
      if len(request.form) != 3:
         result = []
         for nazev,p in zip(nazvy_tlacitek,piny):
            result.append([nazev,p[1]])
         return render_template("index.html",result=result)
      else:
         return redirect(url_for("index"))
   return redirect(url_for("login"))

@app.route("/register/<int:password>")
def registrace(password):
   if password == 69420:
      return render_template("registrace.html")
   return redirect(url_for("login"))

@app.route("/login")
def login():
   if not request.remote_addr in ip:
      return render_template("login.html")
   else: return redirect(url_for("index"))

@app.route("/check")
def check():
   if request.remote_addr in ip:
      conn = sqlite3.connect("user.db")
      c = conn.cursor()
      c.execute("SELECT username FROM Users")
      db = c.fetchall()
      for data in db:
         print(data)
   return redirect(url_for("login"))

@app.route("/logout")
def logout():
   try:
      ip.remove(request.remote_addr)
   except ValueError:
      return redirect(url_for("login"))
   return redirect(url_for("login"))

if __name__ == '__main__':
   app.run(host = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0], port = 5000)