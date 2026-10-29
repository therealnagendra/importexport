from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from app.db import get_db
from app.decorators import csrf_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Enter both username and password.', 'error')
            return render_template('login.html')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid credentials.', 'error')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['username'] = user['username']
        session['csrf_token'] = __import__('secrets').token_hex(16)
        flash('Login successful.', 'success')
        return redirect('/dashboard')

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@csrf_required
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/login')
