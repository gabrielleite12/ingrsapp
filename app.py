from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo_super_secreto"
DB_PATH = "database.db"

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS ingressos (id INTEGER PRIMARY KEY, codigo TEXT, usado INTEGER DEFAULT 0)")
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', '1234')")
        cursor.execute("INSERT INTO ingressos (codigo, usado) VALUES ('INGRS123', 0), ('INGRS456', 1)")
        conn.commit()
        conn.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        pwd = request.form["senha"]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (user, pwd))
        result = cursor.fetchone()
        conn.close()
        if result:
            session["logado"] = True
            return redirect(url_for("scanner"))
        else:
            return render_template("login.html", erro="Usuário ou senha inválidos")
    return render_template("login.html")

@app.route("/scanner")
def scanner():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return render_template("scanner.html")

@app.route("/validar", methods=["POST"])
def validar():
    codigo = request.form["codigo"]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT usado FROM ingressos WHERE codigo=?", (codigo,))
    result = cursor.fetchone()
    if not result:
        status = "❌ Código inválido"
    elif result[0] == 1:
        status = "⚠️ Ingresso já usado"
    else:
        cursor.execute("UPDATE ingressos SET usado=1 WHERE codigo=?", (codigo,))
        conn.commit()
        status = "✅ Entrada liberada"
    conn.close()
    return status

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
