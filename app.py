from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo_super_secreto"
DB_PATH = "ingrs.db"  # Seu arquivo real

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingressos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                usado INTEGER DEFAULT 0
            )
        """)
        # Exemplo: Cria admin só se não existir
        cursor.execute("SELECT 1 FROM usuarios WHERE usuario = 'admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"].strip()
        pwd = request.form["senha"].strip()
        if not user or not pwd:
            flash("Preencha usuário e senha", "error")
            return render_template("login.html")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (user, pwd))
        user_db = cursor.fetchone()
        conn.close()

        if user_db:
            session["logado"] = True
            session["usuario"] = user_db["usuario"]
            return redirect(url_for("scanner"))
        else:
            flash("Usuário ou senha inválidos", "error")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/scanner")
def scanner():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return render_template("scanner.html", usuario=session.get("usuario"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/validar", methods=["POST"])
def validar():
    codigo = request.form.get("codigo", "").strip()
    if not codigo:
        return "❌ Código inválido"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT usado FROM ingressos WHERE codigo = ?", (codigo,))
    ingresso = cursor.fetchone()

    if not ingresso:
        status = "❌ Código inválido"
    elif ingresso["usado"] == 1:
        status = "⚠️ Ingresso já usado"
    else:
        cursor.execute("UPDATE ingressos SET usado = 1 WHERE codigo = ?", (codigo,))
        conn.commit()
        status = "✅ Entrada liberada"
    conn.close()
    return status

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
