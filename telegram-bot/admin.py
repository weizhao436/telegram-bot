from flask import Flask, render_template, request, redirect, flash, url_for
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import sqlite3
from config import config
from bot import update_all_keyboards
import asyncio

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Create admin interface
admin = Admin(app, name='Bot Admin', template_mode='bootstrap3')

# User model for authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == config.ADMIN_USERNAME:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def get_db_connection():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    buttons = conn.execute('SELECT * FROM buttons').fetchall()
    conn.close()
    return render_template('index.html', buttons=buttons)

@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        text = request.form['text']
        response = request.form['response']
        media_type = request.form.get('media_type', 'text')
        media_url = request.form.get('media_url', '')
        
        if not text or not response:
            flash('请填写所有字段')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO buttons (text, response, media_type, media_url) VALUES (?, ?, ?, ?)',
                         (text, response, media_type, media_url))
            conn.commit()
            conn.close()
            # 更新所有用户的键盘
            run_async(update_all_keyboards())
            flash('按钮添加成功')
            return redirect('/')
    
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    conn = get_db_connection()
    button = conn.execute('SELECT * FROM buttons WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        text = request.form['text']
        response = request.form['response']
        media_type = request.form.get('media_type', 'text')
        media_url = request.form.get('media_url', '')
        
        if not text or not response:
            flash('请填写所有字段')
        else:
            conn.execute('UPDATE buttons SET text = ?, response = ?, media_type = ?, media_url = ? WHERE id = ?',
                         (text, response, media_type, media_url, id))
            conn.commit()
            conn.close()
            # 更新所有用户的键盘
            run_async(update_all_keyboards())
            flash('按钮更新成功')
            return redirect('/')
    
    conn.close()
    return render_template('edit.html', button=button)

@app.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM buttons WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    # 更新所有用户的键盘
    run_async(update_all_keyboards())
    flash('按钮删除成功')
    return redirect('/')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    
    # Create buttons table
    c.execute('''
        CREATE TABLE IF NOT EXISTS buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            response TEXT NOT NULL,
            media_type TEXT DEFAULT 'text',
            media_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(host='0.0.0.0', port=5000)
