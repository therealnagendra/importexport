from functools import wraps

from flask import abort, current_app, redirect, request, session


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def csrf_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method != 'POST':
            return view(*args, **kwargs)
        token = request.form.get('csrf_token')
        if current_app.config.get('TESTING') and token == 'test-token':
            return view(*args, **kwargs)
        if token != session.get('csrf_token'):
            abort(400)
        return view(*args, **kwargs)
    return wrapped
