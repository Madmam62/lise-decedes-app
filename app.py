from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'lise2026'

def get_db_connection():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS decedes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cotiseurs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    init_db()  # CRÉE TABLES AUTOMATIQUE
    conn = get_db_connection()
    decedes = [row['nom'] for row in conn.execute('SELECT nom FROM decedes ORDER BY nom').fetchall()]
    cotiseurs = [row['nom'] for row in conn.execute('SELECT nom FROM cotiseurs ORDER BY nom').fetchall()]
    conn.close()
    return render_template('index.html', decedes=decedes, cotiseurs=cotiseurs)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session:
        if request.method == 'POST' and request.form.get('mdp') == 'admin123':
            session['logged_in'] = True
            init_db()
            return redirect(url_for('admin'))
        return '''
        <form method=post style="max-width:300px;margin:50px auto;">
        <h2>Admin (admin123)</h2>
        <input name=mdp type=password style="width:100%;padding:10px;">
        <br><button type=submit style="width:100%;padding:10px;background:blue;color:white;">Entrer</button>
        </form><a href="/">← Public</a>
        '''
    
    init_db()
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        typ = request.form.get('type')
        if nom:
            conn = get_db_connection()
            conn.execute(f'INSERT OR IGNORE INTO {typ} (nom) VALUES (?)', (nom,))
            conn.commit()
            conn.close()
        return redirect(url_for('admin'))
    
    conn = get_db_connection()
    decedes = [row['nom'] for row in conn.execute('SELECT nom FROM decedes ORDER BY nom').fetchall()]
    cotiseurs = [row['nom'] for row in conn.execute('SELECT nom FROM cotiseurs ORDER BY nom').fetchall()]
    conn.close()
    return render_template('admin.html', decedes=decedes, cotiseurs=cotiseurs)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/delete_decede/<nom>')
def delete_decede(nom):
    init_db()
    conn = get_db_connection()
    conn.execute('DELETE FROM decedes WHERE nom = ?', (nom,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete_cotiseur/<nom>')
def delete_cotiseur(nom):
    init_db()
    conn = get_db_connection()
    conn.execute('DELETE FROM cotiseurs WHERE nom = ?', (nom,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/move_decede_to_cotiseur/<nom>')
def move_decede_to_cotiseur(nom):
    init_db()
    conn = get_db_connection()
    conn.execute('DELETE FROM decedes WHERE nom = ?', (nom,))
    conn.execute('INSERT OR IGNORE INTO cotiseurs (nom) VALUES (?)', (nom,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/move_cotiseur_to_decede/<nom>')
def move_cotiseur_to_decede(nom):
    init_db()
    conn = get_db_connection()
    conn.execute('DELETE FROM cotiseurs WHERE nom = ?', (nom,))
    conn.execute('INSERT OR IGNORE INTO decedes (nom) VALUES (?)', (nom,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
