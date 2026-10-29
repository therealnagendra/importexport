from flask import Blueprint, flash, redirect, render_template, request

from app.db import get_db
from app.decorators import csrf_required, login_required

parties_bp = Blueprint('parties', __name__)


@parties_bp.route('/parties')
@login_required
def list_parties():
    db = get_db()
    term = request.args.get('q', '').strip()
    party_type = request.args.get('party_type', '')
    where = []
    params = []
    if term:
        where.append('(company_name LIKE ? OR contact_person LIKE ? OR email LIKE ?)')
        params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
    if party_type:
        where.append('party_type = ?')
        params.append(party_type)
    sql = 'SELECT * FROM parties'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY company_name'
    rows = db.execute(sql, params).fetchall()
    return render_template('parties/list.html', rows=rows, q=term, party_type=party_type)


@parties_bp.route('/parties/new', methods=['GET', 'POST'])
@login_required
@csrf_required
def create_party():
    db = get_db()
    if request.method == 'GET':
        return render_template('parties/form.html', party=None)
    data = request.form
    db.execute('''
        INSERT INTO parties (company_name, party_type, contact_person, email, telephone, address, country, tax_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('company_name'), data.get('party_type'), data.get('contact_person'), data.get('email'),
          data.get('telephone'), data.get('address'), data.get('country'), data.get('tax_id'), data.get('notes')))
    db.commit()
    flash('Party added.', 'success')
    return redirect('/parties')


@parties_bp.route('/parties/<int:party_id>/edit', methods=['GET', 'POST'])
@login_required
@csrf_required
def edit_party(party_id):
    db = get_db()
    party = db.execute('SELECT * FROM parties WHERE id = ?', (party_id,)).fetchone()
    if not party:
        flash('Party not found.', 'error')
        return redirect('/parties')
    if request.method == 'GET':
        return render_template('parties/form.html', party=party)
    data = request.form
    db.execute('''
        UPDATE parties SET company_name = ?, party_type = ?, contact_person = ?, email = ?, telephone = ?,
        address = ?, country = ?, tax_id = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (data.get('company_name'), data.get('party_type'), data.get('contact_person'), data.get('email'),
          data.get('telephone'), data.get('address'), data.get('country'), data.get('tax_id'), data.get('notes'), party_id))
    db.commit()
    flash('Party updated.', 'success')
    return redirect('/parties')


@parties_bp.route('/parties/<int:party_id>/delete', methods=['POST'])
@login_required
@csrf_required
def delete_party(party_id):
    db = get_db()
    existing = db.execute('SELECT COUNT(*) AS count FROM shipments WHERE importer_id = ? OR exporter_id = ?', (party_id, party_id)).fetchone()['count']
    if existing:
        flash('This party is used in existing shipments and cannot be deleted.', 'error')
        return redirect('/parties')
    db.execute('DELETE FROM parties WHERE id = ?', (party_id,))
    db.commit()
    flash('Party deleted.', 'success')
    return redirect('/parties')
