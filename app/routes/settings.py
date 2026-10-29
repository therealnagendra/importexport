from flask import Blueprint, render_template

from app.db import get_db
from app.decorators import admin_required, login_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
@admin_required
def settings():
    db = get_db()
    rows = db.execute('SELECT * FROM application_settings ORDER BY key').fetchall()
    return render_template('settings/list.html', rows=rows)
