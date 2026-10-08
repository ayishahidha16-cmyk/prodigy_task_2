from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "prodigy_task_2_secret"


def get_db():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Username already exists!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect("/dashboard")

        return "Invalid username or password!"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    conn = get_db()
    employees = conn.execute(
        "SELECT * FROM employees"
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        employees=employees
    )


@app.route("/employee/add", methods=["GET", "POST"])
def add_employee():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        position = request.form["position"]

        if not name or not email or not phone or not department or not position:
            return "All fields are required!"

        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO employees
                (name, email, phone, department, position)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, phone, department, position))

            conn.commit()
            conn.close()

            return redirect("/dashboard")

        except sqlite3.IntegrityError:
            return "Email already exists!"

    return render_template("employee.html")


@app.route("/employee/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    if "username" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        position = request.form["position"]

        conn.execute("""
            UPDATE employees
            SET name=?, email=?, phone=?, department=?, position=?
            WHERE id=?
        """, (name, email, phone, department, position, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "employee.html",
        employee=employee
    )


@app.route("/employee/delete/<int:id>")
def delete_employee(id):
    if "username" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)