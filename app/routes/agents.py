from flask import Blueprint, flash, redirect, render_template, request

from app.db import get_db
from app.decorators import csrf_required, login_required

agents_bp = Blueprint('agents', __name__)


@agents_bp.route('/agents')
@login_required
def list_agents():
    db = get_db()
    term = request.args.get('q', '').strip()
    agent_type = request.args.get('agent_type', '')
    where = []
    params = []
    if term:
        where.append('(company_name LIKE ? OR contact_person LIKE ? OR email LIKE ?)')
        params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
    if agent_type:
        where.append('agent_type = ?')
        params.append(agent_type)
    sql = 'SELECT * FROM agents'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY company_name'
    rows = db.execute(sql, params).fetchall()
    return render_template('agents/list.html', rows=rows, q=term, agent_type=agent_type)


@agents_bp.route('/agents/new', methods=['GET', 'POST'])
@login_required
@csrf_required
def create_agent():
    db = get_db()
    if request.method == 'GET':
        return render_template('agents/form.html', agent=None)
    data = request.form
    db.execute('''
        INSERT INTO agents (company_name, agent_type, contact_person, email, telephone, office_address, country, license_reference, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('company_name'), data.get('agent_type'), data.get('contact_person'), data.get('email'),
          data.get('telephone'), data.get('office_address'), data.get('country'), data.get('license_reference'), data.get('notes')))
    db.commit()
    flash('Agent added.', 'success')
    return redirect('/agents')


@agents_bp.route('/agents/<int:agent_id>/edit', methods=['GET', 'POST'])
@login_required
@csrf_required
def edit_agent(agent_id):
    db = get_db()
    agent = db.execute('SELECT * FROM agents WHERE id = ?', (agent_id,)).fetchone()
    if not agent:
        flash('Agent not found.', 'error')
        return redirect('/agents')
    if request.method == 'GET':
        return render_template('agents/form.html', agent=agent)
    data = request.form
    db.execute('''
        UPDATE agents SET company_name = ?, agent_type = ?, contact_person = ?, email = ?, telephone = ?,
        office_address = ?, country = ?, license_reference = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (data.get('company_name'), data.get('agent_type'), data.get('contact_person'), data.get('email'),
          data.get('telephone'), data.get('office_address'), data.get('country'), data.get('license_reference'), data.get('notes'), agent_id))
    db.commit()
    flash('Agent updated.', 'success')
    return redirect('/agents')


@agents_bp.route('/agents/<int:agent_id>/delete', methods=['POST'])
@login_required
@csrf_required
def delete_agent(agent_id):
    db = get_db()
    existing = db.execute('SELECT COUNT(*) AS count FROM shipments WHERE agent_id = ?', (agent_id,)).fetchone()['count']
    if existing:
        flash('This agent is linked to shipments and cannot be deleted.', 'error')
        return redirect('/agents')
    db.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
    db.commit()
    flash('Agent deleted.', 'success')
    return redirect('/agents')
