from flask import Flask, request, render_template, make_response, redirect, url_for
import hashlib
import os
import jwt
import json
import re
import secrets
from datetime import datetime, timedelta

from config import JWT_SECRET, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

ADMIN_PASSWORD_HASH = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()

BLOCKED_PATHS = [
    'admin.html',
    'base.html', 
    'config.py',
    '.env',
    '\.html$'
]

def is_path_allowed(file_path):
    """Проверяет, разрешен ли путь для чтения через LFI"""
    # Нормализуем путь
    normalized_path = os.path.normpath(file_path).lower()
    
    # Проверяем запрещенные паттерны
    for pattern in BLOCKED_PATHS:
        if re.search(pattern, normalized_path):
            return False
    
    return True

# Кастомные фильтры для Jinja2
@app.template_filter('datetime_from_timestamp')
def datetime_from_timestamp(s):
    return datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('tojson')
def tojson_filter(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def generate_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'role': 'admin'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

def log_access(username, ip, success, max_lines=37):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"
    log_entry = f"{timestamp} - {ip} - {username} - {status}\n"
    
    os.makedirs('logs', exist_ok=True)
    log_file = 'logs/access.log'
    
    # Читаем текущие логи
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Добавляем новую запись
    lines.append(log_entry)
    
    # Если строк больше max_lines, оставляем только последние max_lines
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    
    # Записываем обратно
    with open(log_file, 'w') as f:
        f.writelines(lines)

def check_parameter(param):
    if 'admin' in param:
        return False
    if 'sercret' in param:
        return False
    
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        client_ip = request.remote_addr
        
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        if username == 'admin' and password_hash == ADMIN_PASSWORD_HASH:
            token = generate_jwt_token(username)
            log_access(username, client_ip, True)
            
            response = make_response(redirect(url_for('admin_panel')))
            response.set_cookie('jwt_token', token)
            return response
        else:
            log_access(username, client_ip, False)
            error = "Неверные логин или пароль"
    
    return render_template('login.html', error=error)

@app.route('/logs')
def view_logs():
    log_file = request.args.get('file', 'access.log')

    # Защита от LFI уязвимости для критичных файлов
    if not is_path_allowed(log_file):
        logs = "🚫 Доступ к этому файлу запрещен"
        return render_template('logs.html', logs="error", error="Доступ запрещен")
    
    try:
        with open(f'logs/{log_file}', 'r') as f:
            logs = f.read()
    except Exception as e:
        logs = f"Ошибка чтения файла: {str(e)}"
    
    return render_template('logs.html', logs=logs)

@app.route('/admin')
def admin_panel():
    token = request.cookies.get('jwt_token')
    payload = verify_jwt_token(token) if token else None
    
    return render_template('admin.html', payload=payload)

@app.route('/logout')
def logout():
    """Выход из системы - удаляем JWT токен"""
    response = make_response(redirect(url_for('login')))
    response.set_cookie('jwt_token', '', expires=0)  # Удаляем куку
    return response

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    
    # with open('secret.txt', 'w') as f:
    #     f.write('*****************************************************\n')
    
    app.run(host='0.0.0.0', port=8080, debug=True)