from flask import Flask, redirect, url_for, request, render_template, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'feijoada'

@app.route('/')
@app.route('/index')
def index():
    if 'id_usuario_logado' in session:
        with sqlite3.connect('database.db') as usuarios:
            cursor = usuarios.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['id_usuario_logado'],))
            data = cursor.fetchone()
            return render_template('paginas/home.html',usuario=data[1])
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
            data = cursor.fetchone()
            if data:
                session['id_usuario_logado'] = data[0]
                return redirect(url_for('home', id=data[0]))
            flash('Usuário ou senha incorretos')
            return redirect(url_for('index'))
        
    else:
        user = request.args.get('username')
        return render_template('paginas/home.html',usuario=user)
    
@app.route('/home/<int:id>')
def home(id):
    with sqlite3.connect('database.db') as usuarios:
        cursor = usuarios.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
        data = cursor.fetchone()
    return render_template('paginas/home.html',usuario=data[1])

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

@app.route('/config', methods=['GET'])
def config():
    with sqlite3.connect('database.db') as usuarios:
        cursor = usuarios.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['id_usuario_logado'],))
        data = cursor.fetchone()
        return render_template('paginas/configuracoes.html', nome_completo=data[1], nome_usuario=data[2], email=data[3])

@app.route('/logout')
def logout():
    session.pop('id_usuario_logado', None)
    return redirect(url_for('index'))

@app.route('/redefinir_senha', methods = ['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        if 'id_usuario_logado' in session:
            senha_atual = request.form['current_pw']
        else:
            email = request.form['email']
        nova_senha = request.form['new_pw']
        confirm_senha = request.form['confirm_pw']

        with sqlite3.connect('database.db') as usuarios:
            cursor = usuarios.cursor()
            if 'id_usuario_logado' in session:
                cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['id_usuario_logado'],))
            else:
                cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            data = cursor.fetchone()
            if 'id_usuario_logado' in session:
                if data[4] != senha_atual:
                    flash('Senha atual incorreta')
                    return redirect(url_for('config'))
            else:
                if not data:
                    flash('E-mail não cadastrado no nosso sistema!')
                    return redirect(url_for('redefinir_senha'))
            if nova_senha != confirm_senha:
                flash('Senhas não conferem')
                if 'id_usuario_logado' in session:
                    return redirect(url_for('config'))
                return redirect(url_for('redefinir_senha'))

            if 'id_usuario_logado' in session:
                cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, session['id_usuario_logado']))
                usuarios.commit()
                flash('Senha alterada com sucesso!')
                return redirect(url_for('config'))

            cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (nova_senha, email))
            usuarios.commit()
            flash('Senha alterada com sucesso!')
            return redirect(url_for('index'))
        
    return render_template('paginas/redefinir-senha.html')

@app.route('/alterar_dados', methods=['POST'])
def alterar_dados():
    nome_completo = request.form['name']
    nome_usuario = request.form['username']
    email = request.form['email']

    with sqlite3.connect('database.db') as usuarios:
        cursor = usuarios.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['id_usuario_logado'],))
        data = cursor.fetchone()
        if data[1] != nome_completo:
            cursor.execute("UPDATE usuarios SET nome_completo = ? WHERE id = ?", (nome_completo, session['id_usuario_logado']))
        if data[2] != nome_usuario:
            cursor.execute("UPDATE usuarios SET nome_usuario = ? WHERE id = ?", (nome_usuario, session['id_usuario_logado']))
        if data[3] != email:
            cursor.execute("UPDATE usuarios SET email = ? WHERE id = ?", (email, session['id_usuario_logado']))
        usuarios.commit()
        flash('Dados alterados com sucesso!')
        return redirect(url_for('config')) 

@app.route('/excluir_conta')
def excluir_conta():
    with sqlite3.connect('database.db') as usuarios:
        cursor = usuarios.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (session['id_usuario_logado'],))
        usuarios.commit()
        flash('Conta excluída! Redirecionando a página inicial...')
        session.pop('id_usuario_logado', None)
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()