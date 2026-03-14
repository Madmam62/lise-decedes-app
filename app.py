from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_changez_la'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS decedes (nom TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cotiseurs (nom TEXT UNIQUE)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    decedes = [row[0] for row in c.execute('SELECT nom FROM decedes ORDER BY nom').fetchall()]
    cotiseurs = [row[0] for row in c.execute('SELECT nom FROM cotiseurs ORDER BY nom').fetchall()]
    conn.close()
    return render_template('index.html', decedes=decedes, cotiseurs=cotiseurs)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'mdp' not in session:
        if request.method == 'POST' and request.form['mdp'] == 'admin123':
            session['mdp'] = True
            return redirect(url_for('admin'))
        return '''
        <form method=post><input name=mdp placeholder="Mot de passe admin"><input type=submit value="Entrer"></form>
        '''
    
    if request.method == 'POST':
        nom = request.form['nom']
        type_list = request.form['type']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(f'INSERT OR IGNORE INTO {"decedes" if type_list=="decedes" else "cotiseurs"} (nom) VALUES (?)', (nom,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    
    return render_template('admin.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
