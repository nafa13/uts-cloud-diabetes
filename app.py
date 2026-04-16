from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==========================================
# FUNGSI KONEKSI KE AWS RDS (AUTO-SWITCH: LOKAL & EC2)
# ==========================================
DB_HOST = os.environ.get('DB_HOST', 'database-1.cpw6wmmca51b.ap-southeast-2.rds.amazonaws.com')
DB_USER = os.environ.get('DB_USER', 'adminnaufal')
DB_PASS = os.environ.get('DB_PASSWORD', 'Fal130404')
DB_NAME = 'db_diabetes_uts'

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def init_db():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = db.cursor()
        # FIX: Gunakan backtick (`) untuk nama database yang mengandung tanda strip (-) atau underscore
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cursor.execute(f"USE `{DB_NAME}`")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS laporan (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama VARCHAR(255) NOT NULL,
                kadar_gula INT NOT NULL,
                keluhan TEXT NOT NULL,
                file_url TEXT,
                risiko VARCHAR(50)
            )
        ''')
        db.commit()
        cursor.close()
        db.close()
        print("✅ Database RDS MySQL siap!")
    except Exception as e:
        print(f"❌ Error Init DB: {e}")

# Jalankan saat aplikasi mulai
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
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO laporan (nama, kadar_gula, keluhan, file_url, risiko) VALUES (%s, %s, %s, %s, %s)",
                           (nama, kadar_gula, keluhan, file_url, risiko))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Error DB Insert: {e}")

        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    search = request.args.get('search', '')
    laporan_data = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        
        if search:
            cursor.execute("SELECT * FROM laporan WHERE nama LIKE %s", ('%' + search + '%',))
        else:
            cursor.execute("SELECT * FROM laporan")
            
        laporan_data = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error DB Select: {e}")
        
    return render_template('dashboard.html', data=laporan_data, search=search)

@app.route('/delete/<int:id>')
def delete(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM laporan WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error DB Delete: {e}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)