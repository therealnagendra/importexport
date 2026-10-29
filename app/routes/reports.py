from flask import Blueprint, request

from app.db import get_db
from app.decorators import login_required
from app.utils import export_csv_response

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def reports():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments ORDER BY created_at DESC').fetchall()
    from flask import render_template
    return render_template('reports/list.html', shipments=shipments)


@reports_bp.route('/reports/export')
@login_required
def export_report():
    db = get_db()
    report_type = request.args.get('type', 'shipments')
    if report_type == 'expenses':
        rows = db.execute('SELECT category, description, amount, currency, payment_status FROM expenses ORDER BY expense_date DESC').fetchall()
        fieldnames = ['category', 'description', 'amount', 'currency', 'payment_status']
        return export_csv_response([dict(r) for r in rows], fieldnames, 'expenses_report.csv')
    rows = db.execute('SELECT reference_no, shipment_type, shipment_status, product_description, origin_country, destination_country, assigned_staff FROM shipments ORDER BY created_at DESC').fetchall()
    fieldnames = ['reference_no', 'shipment_type', 'shipment_status', 'product_description', 'origin_country', 'destination_country', 'assigned_staff']
    return export_csv_response([dict(r) for r in rows], fieldnames, 'shipments_report.csv')
