from flask import Flask, render_template, request, redirect, session
import json
import os
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Ensure users.json exists
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        users = load_users()

        if username in users:
            return "User already exists!"

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        users[username] = {
            "password": hashed_password.decode("utf-8"),
            "role": role
        }

        save_users(users)
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            stored_password = users[username]["password"].encode("utf-8")

            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                session["user"] = username
                session["role"] = users[username]["role"]

                if users[username]["role"] == "admin":
                    return redirect("/admin")
                else:
                    return redirect("/user")

        return "Invalid Credentials!"

    return render_template("login.html")

@app.route("/admin")
def admin():
    if "user" in session and session["role"] == "admin":
        users = load_users()
        return render_template("admin.html", users=users)
    return redirect("/login")

@app.route("/user")
def user():
    if "user" in session:
        return render_template("user.html", username=session["user"])
    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
