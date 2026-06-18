from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Preethi@2006",
        database="attendance_db"
    )

def calculate_risk(p):
    if p < 65:
        return "High"
    elif p < 75:
        return "Medium"
    else:
        return "Low"

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

# ADD
@app.route("/add", methods=["POST"])
def add_attendance():
    try:
        d = request.json

        register_no = d["register_no"]
        name = d["name"]
        subject = d["subject"]
        attended = int(d["attended"])
        total = int(d["total"])

        if attended < 0 or total <= 0 or attended > total:
            return jsonify(success=False, error="Invalid attendance values")

        percentage = round((attended / total) * 100, 2)
        risk = calculate_risk(percentage)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO attendance
            (user_id, register_no, name, subject, attended, total, percentage, risk)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session["user_id"],
            register_no, name, subject,
            attended, total, percentage, risk
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(success=True)

    except Exception as e:
        print("ERROR:", e)
        return jsonify(success=False, error=str(e))

# READ
@app.route("/students")
def students():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM attendance ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(rows)

# DELETE
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(success=True)

# STATS
@app.route("/stats")
def stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM attendance")
    total = cur.fetchone()[0]

    cur.execute("SELECT AVG(percentage) FROM attendance")
    avg = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM attendance WHERE risk='High'")
    high = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify(total=total, average=round(avg, 2), high_risk=high)

# AUTH
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s", (u,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], p):
            session["user_id"] = user["id"]
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users(username,password_hash) VALUES(%s,%s)", (u,p))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/login")
        except:
            return render_template("register.html", error="Username exists")

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
