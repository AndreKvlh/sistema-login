from flask import Flask, redirect, url_for, request, render_template, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'feijoada'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome_completo TEXT, nome_usuario TEXT, email TEXT, senha TEXT)')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        senha = request.form['password']
        with sqlite3.connect('database.db') as usuarios:
            cursor = usuarios.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE nome_usuario = ? AND senha = ?", (user, senha))
            if cursor.fetchone():
                return render_template('paginas/home.html',usuario=user)
            flash('Usuário ou senha incorretos')
            return redirect(url_for('index'))
        
    else:
        user = request.args.get('username')
        return render_template('paginas/home.html',usuario=user)
    
@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        nome_completo = request.form['name']
        nome_usuario = request.form['username']
        email = request.form['email']
        senha = request.form['new_pw']
        if senha != request.form['confirm_pw']:
            flash('Senhas não conferem')
            return redirect(url_for('cadastro'))

        with sqlite3.connect('database.db') as usuarios:
            cursor = usuarios.cursor()
            # Verifica se o usuário existe na db
            cursor.execute("SELECT * FROM usuarios WHERE nome_usuario = ?", (nome_usuario,))
            if cursor.fetchone():
                flash('Usuário já cadastrado')
                return redirect(url_for('cadastro'))
            
            # Verifica se e-mail existe na db
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                flash('E-mail já está sendo utilizado por outra conta')
                return redirect(url_for('cadastro'))

            cursor.execute("INSERT INTO usuarios (nome_completo, nome_usuario, email, senha) VALUES (?, ?, ?, ?)", (nome_completo, nome_usuario, email, senha))
            usuarios.commit()
        return render_template('index.html')
    return render_template('paginas/cadastro.html')

if __name__ == '__main__':
    app.run()