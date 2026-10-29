from flask import Blueprint, flash, redirect, render_template, request, session

from app.db import get_db
from app.decorators import csrf_required, login_required

tracking_bp = Blueprint('tracking', __name__)


@tracking_bp.route('/tracking/<int:shipment_id>')
@login_required
def shipment_tracking(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    if not shipment:
        flash('Shipment not found.', 'error')
        return redirect('/shipments')
    rows = db.execute('''
        SELECT t.*, u.username AS user_name
        FROM tracking_milestones t
        LEFT JOIN users u ON u.id = t.user_id
        WHERE t.shipment_id = ?
        ORDER BY t.milestone_date ASC
    ''', (shipment_id,)).fetchall()
    return render_template('tracking/list.html', shipment=shipment, rows=rows)


@tracking_bp.route('/tracking/<int:shipment_id>/new', methods=['GET', 'POST'])
@login_required
@csrf_required
def add_milestone(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    if not shipment:
        flash('Shipment not found.', 'error')
        return redirect('/shipments')
    if request.method == 'GET':
        return render_template('tracking/form.html', shipment=shipment, milestone=None)
    data = request.form
    db.execute('''
        INSERT INTO tracking_milestones (shipment_id, milestone, milestone_date, location, status, remarks, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (shipment_id, data.get('milestone'), data.get('milestone_date'), data.get('location'), data.get('status'), data.get('remarks'), session['user_id']))
    db.commit()
    flash('Milestone added.', 'success')
    return redirect(f'/tracking/{shipment_id}')
