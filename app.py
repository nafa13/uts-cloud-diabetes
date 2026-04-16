from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('diabetes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            kadar_gula INTEGER NOT NULL,
            keluhan TEXT NOT NULL,
            file_url TEXT,
            risiko TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        nama = request.form['nama']
        kadar_gula = int(request.form['kadar_gula'])
        keluhan = request.form['keluhan']
        
        # FITUR EKSKLUSIF: DETEKSI RISIKO OTOMATIS
        if kadar_gula < 140:
            risiko = "Normal"
        elif 140 <= kadar_gula <= 199:
            risiko = "Pradiabetes"
        else:
            risiko = "Tinggi (Diabetes)"
            
        file = request.files.get('file_lab')
        file_url = ""
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_url = '/' + file_path

        try:
            conn = sqlite3.connect('diabetes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO laporan (nama, kadar_gula, keluhan, file_url, risiko) VALUES (?, ?, ?, ?, ?)",
                           (nama, kadar_gula, keluhan, file_url, risiko))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error DB: {e}")

        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # FITUR SEARCH
    search = request.args.get('search', '')
    laporan_data = []
    
    try:
        conn = sqlite3.connect('diabetes.db')
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        if search:
            # Jika ada kata kunci pencarian, filter berdasarkan nama
            cursor.execute("SELECT * FROM laporan WHERE nama LIKE ?", ('%' + search + '%',))
        else:
            # Jika tidak ada, tampilkan semua
            cursor.execute("SELECT * FROM laporan")
            
        laporan_data = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ Error baca DB: {e}")
        
    return render_template('dashboard.html', data=laporan_data, search=search)

# FITUR DELETE DATA (CRUD)
@app.route('/delete/<int:id>')
def delete(id):
    try:
        conn = sqlite3.connect('diabetes.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM laporan WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error Delete DB: {e}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)