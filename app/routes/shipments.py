from flask import Blueprint, flash, redirect, render_template, request

from app.db import get_db
from app.decorators import csrf_required, login_required
from app.validators import validate_date, validate_required

shipments_bp = Blueprint('shipments', __name__)


@shipments_bp.route('/shipments')
@login_required
def list_shipments():
    db = get_db()
    q = request.args.get('q', '').strip()
    shipment_type = request.args.get('shipment_type', '')
    status = request.args.get('status', '')
    country = request.args.get('country', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    page = max(int(request.args.get('page', 1)), 1)
    limit = 10
    offset = (page - 1) * limit

    filters = []
    params = []
    if q:
        filters.append('(reference_no LIKE ? OR product_description LIKE ? OR importer_id IN (SELECT id FROM parties WHERE company_name LIKE ?) OR exporter_id IN (SELECT id FROM parties WHERE company_name LIKE ?))')
        term = f'%{q}%'
        params.extend([term, term, term, term])
    if shipment_type:
        filters.append('shipment_type = ?')
        params.append(shipment_type)
    if status:
        filters.append('shipment_status = ?')
        params.append(status)
    if country:
        filters.append('(origin_country LIKE ? OR destination_country LIKE ?)')
        params.extend([f'%{country}%', f'%{country}%'])
    if from_date:
        filters.append('shipment_date >= ?')
        params.append(from_date)
    if to_date:
        filters.append('shipment_date <= ?')
        params.append(to_date)

    where_clause = ' WHERE ' + ' AND '.join(filters) if filters else ''
    rows = db.execute(f'''
        SELECT s.*, p.company_name AS importer_name, p2.company_name AS exporter_name, a.company_name AS agent_name
        FROM shipments s
        LEFT JOIN parties p ON p.id = s.importer_id
        LEFT JOIN parties p2 ON p2.id = s.exporter_id
        LEFT JOIN agents a ON a.id = s.agent_id
        {where_clause}
        ORDER BY s.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [limit, offset]).fetchall()

    total = db.execute(f'SELECT COUNT(*) AS count FROM shipments s {where_clause}', params).fetchone()['count']
    parties = db.execute('SELECT id, company_name FROM parties ORDER BY company_name').fetchall()
    agents = db.execute('SELECT id, company_name FROM agents ORDER BY company_name').fetchall()
    return render_template('shipments/list.html', rows=rows, parties=parties, agents=agents, page=page, total=total, q=q, shipment_type=shipment_type, status=status, country=country, from_date=from_date, to_date=to_date)


@shipments_bp.route('/shipments/new', methods=['GET', 'POST'])
@login_required
@csrf_required
def create_shipment():
    db = get_db()
    if request.method == 'GET':
        parties = db.execute('SELECT id, company_name FROM parties ORDER BY company_name').fetchall()
        agents = db.execute('SELECT id, company_name FROM agents ORDER BY company_name').fetchall()
        return render_template('shipments/form.html', shipment=None, parties=parties, agents=agents)

    data = request.form
    try:
        reference_no = validate_required(data.get('reference_no'), 'Shipment reference')
        if db.execute('SELECT 1 FROM shipments WHERE reference_no = ?', (reference_no,)).fetchone():
            raise ValueError('Shipment reference already exists.')
        shipment_type = validate_required(data.get('shipment_type'), 'Shipment type')
        product_description = validate_required(data.get('product_description'), 'Product description')
        db.execute('''
            INSERT INTO shipments (
                reference_no, shipment_type, product_description, importer_id, exporter_id, origin_country,
                destination_country, origin_port, destination_port, hs_code, quantity, unit, invoice_value,
                currency, exchange_rate, invoice_no, invoice_date, shipment_date, expected_arrival, actual_arrival,
                container_no, bl_awb_no, transport_mode, carrier, agent_id, assigned_staff, shipment_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reference_no, shipment_type, product_description, data.get('importer_id') or None, data.get('exporter_id') or None,
              data.get('origin_country'), data.get('destination_country'), data.get('origin_port'), data.get('destination_port'),
              data.get('hs_code'), data.get('quantity') or None, data.get('unit'), data.get('invoice_value') or None,
              data.get('currency') or 'USD', data.get('exchange_rate') or None, data.get('invoice_no'),
              validate_date(data.get('invoice_date'), 'Invoice date'), validate_date(data.get('shipment_date'), 'Shipment date'),
              validate_date(data.get('expected_arrival'), 'Expected arrival'), validate_date(data.get('actual_arrival'), 'Actual arrival'),
              data.get('container_no'), data.get('bl_awb_no'), data.get('transport_mode'), data.get('carrier'), data.get('agent_id') or None,
              data.get('assigned_staff'), data.get('shipment_status') or 'Pending', data.get('notes')))
        db.commit()
        flash('Shipment created successfully.', 'success')
        return redirect('/shipments')
    except ValueError as exc:
        flash(str(exc), 'error')
        parties = db.execute('SELECT id, company_name FROM parties ORDER BY company_name').fetchall()
        agents = db.execute('SELECT id, company_name FROM agents ORDER BY company_name').fetchall()
        return render_template('shipments/form.html', shipment=None, parties=parties, agents=agents)


@shipments_bp.route('/shipments/<int:shipment_id>/edit', methods=['GET', 'POST'])
@login_required
@csrf_required
def edit_shipment(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    if not shipment:
        flash('Shipment not found.', 'error')
        return redirect('/shipments')
    if request.method == 'GET':
        parties = db.execute('SELECT id, company_name FROM parties ORDER BY company_name').fetchall()
        agents = db.execute('SELECT id, company_name FROM agents ORDER BY company_name').fetchall()
        return render_template('shipments/form.html', shipment=shipment, parties=parties, agents=agents)

    data = request.form
    try:
        reference_no = validate_required(data.get('reference_no'), 'Shipment reference')
        existing = db.execute('SELECT id FROM shipments WHERE reference_no = ? AND id != ?', (reference_no, shipment_id)).fetchone()
        if existing:
            raise ValueError('Shipment reference already exists.')
        db.execute('''
            UPDATE shipments SET
                reference_no = ?, shipment_type = ?, product_description = ?, importer_id = ?, exporter_id = ?, origin_country = ?,
                destination_country = ?, origin_port = ?, destination_port = ?, hs_code = ?, quantity = ?, unit = ?, invoice_value = ?,
                currency = ?, exchange_rate = ?, invoice_no = ?, invoice_date = ?, shipment_date = ?, expected_arrival = ?,
                actual_arrival = ?, container_no = ?, bl_awb_no = ?, transport_mode = ?, carrier = ?, agent_id = ?, assigned_staff = ?,
                shipment_status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (reference_no, data.get('shipment_type'), data.get('product_description'), data.get('importer_id') or None,
              data.get('exporter_id') or None, data.get('origin_country'), data.get('destination_country'),
              data.get('origin_port'), data.get('destination_port'), data.get('hs_code'), data.get('quantity') or None,
              data.get('unit'), data.get('invoice_value') or None, data.get('currency') or 'USD', data.get('exchange_rate') or None,
              data.get('invoice_no'), validate_date(data.get('invoice_date'), 'Invoice date'), validate_date(data.get('shipment_date'), 'Shipment date'),
              validate_date(data.get('expected_arrival'), 'Expected arrival'), validate_date(data.get('actual_arrival'), 'Actual arrival'),
              data.get('container_no'), data.get('bl_awb_no'), data.get('transport_mode'), data.get('carrier'), data.get('agent_id') or None,
              data.get('assigned_staff'), data.get('shipment_status') or 'Pending', data.get('notes'), shipment_id))
        db.commit()
        flash('Shipment updated successfully.', 'success')
        return redirect('/shipments')
    except ValueError as exc:
        flash(str(exc), 'error')
        parties = db.execute('SELECT id, company_name FROM parties ORDER BY company_name').fetchall()
        agents = db.execute('SELECT id, company_name FROM agents ORDER BY company_name').fetchall()
        return render_template('shipments/form.html', shipment=shipment, parties=parties, agents=agents)


@shipments_bp.route('/shipments/<int:shipment_id>/delete', methods=['POST'])
@login_required
@csrf_required
def delete_shipment(shipment_id):
    db = get_db()
    if db.execute('SELECT 1 FROM expenses WHERE shipment_id = ?', (shipment_id,)).fetchone():
        flash('Cannot delete shipment because it has linked expense records.', 'error')
        return redirect('/shipments')
    db.execute('DELETE FROM shipments WHERE id = ?', (shipment_id,))
    db.commit()
    flash('Shipment deleted.', 'success')
    return redirect('/shipments')
