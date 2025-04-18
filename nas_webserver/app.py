from flask import Flask, render_template, session, redirect
from flask_mysqldb import MySQL
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = os.getenv('SECRET_KEY') or 'fallback-secret-key'
app.permanent_session_lifetime = timedelta(minutes=30)

# Set upload folder (and create if doesn't exist)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize MySQL
mysql = MySQL(app)
app.extensions['mysql'] = mysql

# Import and register Blueprints
from modules.file_routes import file_bp
from modules.user_routes import user_bp
from modules.monitor_routes import monitor_bp
from modules.backup_routes import backup_bp

app.register_blueprint(file_bp)
app.register_blueprint(user_bp)
app.register_blueprint(monitor_bp)
app.register_blueprint(backup_bp)

# ---------------------------------------
# Basic Page Routes
# ---------------------------------------

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'], role=session.get('role'))

@app.route('/monitor')
def monitor():
    if 'username' not in session:
        return redirect('/login')
    return render_template('monitor.html')

@app.route('/backup')
def backup():
    if 'username' not in session:
        return redirect('/login')
    return render_template('backup.html')

@app.route('/files')
def files_page():
    if 'username' not in session:
        return redirect('/login')
    return render_template('files.html', role=session.get('role'))

# ---------------------------------------
# Run App
# ---------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

