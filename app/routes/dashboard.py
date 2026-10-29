from flask import Blueprint, render_template

from app.db import get_db
from app.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    totals = db.execute('''
        SELECT
            COUNT(*) AS total_shipments,
            SUM(CASE WHEN shipment_type = 'Import' THEN 1 ELSE 0 END) AS import_count,
            SUM(CASE WHEN shipment_type = 'Export' THEN 1 ELSE 0 END) AS export_count,
            SUM(CASE WHEN shipment_status IN ('In Transit', 'Pending', 'Customs Cleared') THEN 1 ELSE 0 END) AS active_count,
            SUM(CASE WHEN shipment_status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
            SUM(CASE WHEN shipment_status = 'Delivered' THEN 1 ELSE 0 END) AS completed_count
        FROM shipments
    ''').fetchone()

    expenses = db.execute('SELECT COALESCE(SUM(amount), 0) AS total_expenses FROM expenses').fetchone()
    recent = db.execute('''
        SELECT s.*, p.company_name AS importer_name, p2.company_name AS exporter_name
        FROM shipments s
        LEFT JOIN parties p ON p.id = s.importer_id
        LEFT JOIN parties p2 ON p2.id = s.exporter_id
        ORDER BY s.created_at DESC
        LIMIT 6
    ''').fetchall()

    status_distribution = db.execute('''
        SELECT shipment_status AS label, COUNT(*) AS value
        FROM shipments
        GROUP BY shipment_status
        ORDER BY value DESC
    ''').fetchall()

    monthly = db.execute('''
        SELECT strftime('%Y-%m', shipment_date) AS month,
               SUM(CASE WHEN shipment_type='Import' THEN 1 ELSE 0 END) AS imports,
               SUM(CASE WHEN shipment_type='Export' THEN 1 ELSE 0 END) AS exports
        FROM shipments
        WHERE shipment_date IS NOT NULL
        GROUP BY strftime('%Y-%m', shipment_date)
        ORDER BY month DESC
        LIMIT 6
    ''').fetchall()

    return render_template('dashboard.html', totals=totals, expense_total=expenses['total_expenses'], recent_shipments=recent, status_distribution=status_distribution, monthly=monthly)
