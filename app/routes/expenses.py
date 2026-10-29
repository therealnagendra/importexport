from flask import Blueprint, flash, redirect, render_template, request

from app.db import get_db
from app.decorators import csrf_required, login_required

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/expenses')
@login_required
def list_expenses():
    db = get_db()
    rows = db.execute('''
        SELECT e.*, s.reference_no AS shipment_reference
        FROM expenses e
        LEFT JOIN shipments s ON s.id = e.shipment_id
        ORDER BY e.expense_date DESC
    ''').fetchall()
    shipments = db.execute('SELECT id, reference_no FROM shipments ORDER BY reference_no').fetchall()
    return render_template('expenses/list.html', rows=rows, shipments=shipments)


@expenses_bp.route('/expenses/new', methods=['GET', 'POST'])
@login_required
@csrf_required
def create_expense():
    db = get_db()
    if request.method == 'GET':
        shipments = db.execute('SELECT id, reference_no FROM shipments ORDER BY reference_no').fetchall()
        return render_template('expenses/form.html', expense=None, shipments=shipments)
    data = request.form
    db.execute('''
        INSERT INTO expenses (shipment_id, category, description, amount, currency, expense_date, vendor, payment_status, payment_reference, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('shipment_id'), data.get('category'), data.get('description'), data.get('amount'), data.get('currency'),
          data.get('expense_date'), data.get('vendor'), data.get('payment_status'), data.get('payment_reference'), data.get('notes')))
    db.commit()
    flash('Expense added.', 'success')
    return redirect('/expenses')


@expenses_bp.route('/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
@csrf_required
def edit_expense(expense_id):
    db = get_db()
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    if not expense:
        flash('Expense not found.', 'error')
        return redirect('/expenses')
    if request.method == 'GET':
        shipments = db.execute('SELECT id, reference_no FROM shipments ORDER BY reference_no').fetchall()
        return render_template('expenses/form.html', expense=expense, shipments=shipments)
    data = request.form
    db.execute('''
        UPDATE expenses SET shipment_id = ?, category = ?, description = ?, amount = ?, currency = ?, expense_date = ?, vendor = ?,
        payment_status = ?, payment_reference = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (data.get('shipment_id'), data.get('category'), data.get('description'), data.get('amount'), data.get('currency'),
          data.get('expense_date'), data.get('vendor'), data.get('payment_status'), data.get('payment_reference'), data.get('notes'), expense_id))
    db.commit()
    flash('Expense updated.', 'success')
    return redirect('/expenses')


@expenses_bp.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
@csrf_required
def delete_expense(expense_id):
    db = get_db()
    db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    db.commit()
    flash('Expense deleted.', 'success')
    return redirect('/expenses')
