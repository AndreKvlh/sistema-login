from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        return render_template('paginas/home.html',usuario=user)
    else:
        user = request.args.get('username')
        return render_template('paginas/home.html',usuario=user)

if __name__ == '__main__':
    app.run()