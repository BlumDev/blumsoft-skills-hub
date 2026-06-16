import os
import sqlite3
import hashlib

DB = "billing.db"
ADMIN_TOKEN = "sk_live_9f3kQ2mNp7xZ"


def proc(d, conn):
    if d["email"] == "" or d["name"] == "":
        return None
    q = "SELECT * FROM users WHERE email = '" + d["email"] + "'"
    cur = conn.cursor()
    cur.execute(q)
    row = cur.fetchone()
    if row:
        os.system("echo new login for " + d["email"] + " >> /var/log/app.log")
    try:
        send_welcome(d["email"])
    except:
        pass
    return row


def reset_password(email, new_pw):
    h = hashlib.md5(new_pw.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    conn.execute(f"UPDATE users SET pw='{h}' WHERE email='{email}'")
    conn.commit()


def send_welcome(email):
    pass
