from getpass import getpass
from datetime import date, timedelta

import click
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db, init_db

app = create_app()


@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        init_db()
        click.echo('Database initialized.')


@app.cli.command('create-admin')
def create_admin_command():
    username = click.prompt('Username', prompt_suffix=': ')
    password = getpass('Password: ')
    if not username or not password:
        raise click.ClickException('Username and password are required.')
    with app.app_context():
        db = get_db()
        if db.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone():
            raise click.ClickException('That username already exists.')
        db.execute('INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)',
                   (username, generate_password_hash(password), 'admin', username))
        db.commit()
        click.echo(f'Administrator account created for {username}.')


@app.cli.command('seed-demo')
@click.option('--dry-run', is_flag=True, default=False)
def seed_demo_command(dry_run):
    with app.app_context():
        db = get_db()
        references = ('DEMO-IMP-001', 'DEMO-EXP-001', 'DEMO-IMP-002', 'DEMO-EXP-002')
        existing = db.execute(
            'SELECT reference_no FROM shipments WHERE reference_no IN (?, ?, ?, ?)',
            references
        ).fetchall()
        existing_references = {row['reference_no'] for row in existing}
        if dry_run:
            click.echo(f'Dry run: {len(references) - len(existing_references)} demo shipment(s) would be inserted.')
            return

        def ensure_record(table, name, fields, values):
            row = db.execute(f'SELECT id FROM {table} WHERE company_name = ?', (name,)).fetchone()
            if row:
                return row['id']
            columns = ', '.join(('company_name', *fields))
            placeholders = ', '.join('?' for _ in range(len(fields) + 1))
            cursor = db.execute(
                f'INSERT INTO {table} ({columns}) VALUES ({placeholders})',
                (name, *values)
            )
            return cursor.lastrowid

        parties = {
            'india_importer': ensure_record(
                'parties', 'Northstar Industrial Imports',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Importer', 'Ananya Mehta', 'ananya@northstar.example', '+91 22 5550 0142', 'India', 'IN-DEMO-001')
            ),
            'germany_exporter': ensure_record(
                'parties', 'Alpine Precision GmbH',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Exporter', 'Lukas Weber', 'lukas@alpine.example', '+49 40 5550 0188', 'Germany', 'DE-DEMO-001')
            ),
            'india_exporter': ensure_record(
                'parties', 'Monsoon Leaf Exports',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Exporter', 'Priya Nair', 'priya@monsoon.example', '+91 484 5550 0195', 'India', 'IN-DEMO-002')
            ),
            'uae_importer': ensure_record(
                'parties', 'Crescent Bay Trading FZE',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Importer', 'Omar Khalid', 'omar@crescent.example', '+971 4 555 0186', 'United Arab Emirates', 'AE-DEMO-001')
            ),
            'us_exporter': ensure_record(
                'parties', 'MedEquip Solutions Inc',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Exporter', 'Maya Thompson', 'maya@medequip.example', '+1 310 555 0164', 'United States', 'US-DEMO-001')
            ),
            'india_buyer': ensure_record(
                'parties', 'Saffron Coast Foods',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Buyer', 'Rohan Das', 'rohan@saffron.example', '+91 33 5550 0107', 'India', 'IN-DEMO-003')
            ),
            'uae_exporter': ensure_record(
                'parties', 'Gulf Looms Trading FZE',
                ('party_type', 'contact_person', 'email', 'telephone', 'country', 'tax_id'),
                ('Exporter', 'Fatima Noor', 'fatima@gulflooms.example', '+971 4 555 0112', 'United Arab Emirates', 'AE-DEMO-002')
            ),
        }
        agents = {
            'bluewave': ensure_record(
                'agents', 'BlueWave Freight Services',
                ('agent_type', 'contact_person', 'email', 'telephone', 'country', 'license_reference'),
                ('Freight', 'Sameer Rao', 'ops@bluewave.example', '+91 22 5550 0201', 'India', 'FREIGHT-DEMO-01')
            ),
            'clearpath': ensure_record(
                'agents', 'ClearPath Customs Brokers',
                ('agent_type', 'contact_person', 'email', 'telephone', 'country', 'license_reference'),
                ('CHA', 'Kavita Iyer', 'clearance@clearpath.example', '+91 44 5550 0202', 'India', 'CHA-DEMO-02')
            ),
        }

        today = date.today()
        shipment_rows = [
            {
                'reference_no': 'DEMO-IMP-001', 'shipment_type': 'Import',
                'product_description': 'CNC machine components', 'importer_id': parties['india_importer'],
                'exporter_id': parties['germany_exporter'], 'origin_country': 'Germany',
                'destination_country': 'India', 'origin_port': 'Hamburg', 'destination_port': 'Nhava Sheva',
                'hs_code': '8466.93', 'quantity': 240, 'unit': 'pcs', 'invoice_value': 84500,
                'currency': 'EUR', 'shipment_date': (today - timedelta(days=12)).isoformat(),
                'expected_arrival': (today + timedelta(days=9)).isoformat(), 'container_no': 'MSCU1234567',
                'bl_awb_no': 'BL-DEMO-24001', 'transport_mode': 'Sea', 'carrier': 'Maersk',
                'agent_id': agents['bluewave'], 'shipment_status': 'In Transit',
                'notes': 'Demo record. Sample values only; replace with actual shipment information.'
            },
            {
                'reference_no': 'DEMO-EXP-001', 'shipment_type': 'Export',
                'product_description': 'Organic Assam tea', 'importer_id': parties['uae_importer'],
                'exporter_id': parties['india_exporter'], 'origin_country': 'India',
                'destination_country': 'United Arab Emirates', 'origin_port': 'Mundra', 'destination_port': 'Jebel Ali',
                'hs_code': '0902.30', 'quantity': 1200, 'unit': 'kg', 'invoice_value': 18900,
                'currency': 'USD', 'shipment_date': (today - timedelta(days=35)).isoformat(),
                'expected_arrival': (today - timedelta(days=22)).isoformat(),
                'actual_arrival': (today - timedelta(days=21)).isoformat(), 'container_no': 'TGHU7654321',
                'bl_awb_no': 'BL-DEMO-24002', 'transport_mode': 'Sea', 'carrier': 'CMA CGM',
                'agent_id': agents['bluewave'], 'shipment_status': 'Delivered',
                'notes': 'Demo record. Sample values only; replace with actual shipment information.'
            },
            {
                'reference_no': 'DEMO-IMP-002', 'shipment_type': 'Import',
                'product_description': 'Diagnostic imaging equipment', 'importer_id': parties['india_importer'],
                'exporter_id': parties['us_exporter'], 'origin_country': 'United States',
                'destination_country': 'India', 'origin_port': 'Los Angeles', 'destination_port': 'Chennai',
                'hs_code': '9022.14', 'quantity': 8, 'unit': 'crates', 'invoice_value': 56200,
                'currency': 'USD', 'shipment_date': (today - timedelta(days=18)).isoformat(),
                'expected_arrival': (today - timedelta(days=2)).isoformat(),
                'container_no': 'OOLU2468135', 'bl_awb_no': 'BL-DEMO-24003',
                'transport_mode': 'Sea', 'carrier': 'Hapag-Lloyd',
                'agent_id': agents['clearpath'], 'shipment_status': 'Customs Cleared',
                'notes': 'Demo record. Sample values only; replace with actual shipment information.'
            },
            {
                'reference_no': 'DEMO-EXP-002', 'shipment_type': 'Export',
                'product_description': 'Handcrafted cotton garments', 'importer_id': parties['india_buyer'],
                'exporter_id': parties['uae_exporter'], 'origin_country': 'United Arab Emirates',
                'destination_country': 'India', 'origin_port': 'Jebel Ali', 'destination_port': 'Kolkata',
                'hs_code': '6204.62', 'quantity': 500, 'unit': 'pcs', 'invoice_value': 12750,
                'currency': 'USD', 'shipment_date': (today + timedelta(days=3)).isoformat(),
                'expected_arrival': (today + timedelta(days=18)).isoformat(),
                'bl_awb_no': 'BL-DEMO-24004', 'transport_mode': 'Sea', 'carrier': 'MSC',
                'agent_id': agents['bluewave'], 'shipment_status': 'Pending',
                'notes': 'Demo record. Sample values only; replace with actual shipment information.'
            },
        ]
        shipment_ids = {}
        for shipment in shipment_rows:
            row = db.execute(
                'SELECT id FROM shipments WHERE reference_no = ?',
                (shipment['reference_no'],)
            ).fetchone()
            if row:
                shipment_ids[shipment['reference_no']] = row['id']
                continue
            columns = ', '.join(shipment)
            placeholders = ', '.join('?' for _ in shipment)
            cursor = db.execute(
                f'INSERT INTO shipments ({columns}) VALUES ({placeholders})',
                tuple(shipment.values())
            )
            shipment_ids[shipment['reference_no']] = cursor.lastrowid

        user = db.execute('SELECT id FROM users ORDER BY id LIMIT 1').fetchone()
        user_id = user['id'] if user else None
        milestones = [
            ('DEMO-IMP-001', 'Booking confirmed', 11, 'Hamburg', 'Completed', 'Container booking confirmed by carrier.'),
            ('DEMO-IMP-001', 'Vessel departed', 7, 'Hamburg', 'Completed', 'Vessel departed origin port.'),
            ('DEMO-IMP-001', 'In transit', 2, 'At sea', 'In Progress', 'Shipment is moving toward destination.'),
            ('DEMO-EXP-001', 'Export customs cleared', 34, 'Mundra', 'Completed', 'Export documentation approved.'),
            ('DEMO-EXP-001', 'Delivered to consignee', 21, 'Dubai', 'Completed', 'Delivery confirmed by consignee.'),
            ('DEMO-IMP-002', 'Arrived at destination port', 4, 'Chennai', 'Completed', 'Vessel arrived at Chennai port.'),
            ('DEMO-IMP-002', 'Import customs cleared', 1, 'Chennai', 'Completed', 'Customs clearance completed.'),
            ('DEMO-EXP-002', 'Booking requested', 0, 'Jebel Ali', 'Booked', 'Awaiting carrier booking confirmation.'),
        ]
        for reference, milestone, days_ago, location, status, remarks in milestones:
            shipment_id = shipment_ids[reference]
            exists = db.execute(
                'SELECT 1 FROM tracking_milestones WHERE shipment_id = ? AND milestone = ?',
                (shipment_id, milestone)
            ).fetchone()
            if not exists:
                milestone_time = (today - timedelta(days=days_ago)).isoformat() + ' 09:00'
                db.execute(
                    '''INSERT INTO tracking_milestones
                       (shipment_id, milestone, milestone_date, location, status, remarks, user_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (shipment_id, milestone, milestone_time, location, status, remarks, user_id)
                )

        expense_rows = [
            ('DEMO-IMP-001', 'Freight', 'Ocean freight charge', 4200, 'EUR', 10, 'BlueWave Freight Services', 'Paid', 'DEMO-PAY-001'),
            ('DEMO-IMP-001', 'Insurance', 'Cargo insurance premium', 380, 'EUR', 9, 'Harbor Mutual Insurance', 'Paid', 'DEMO-PAY-002'),
            ('DEMO-EXP-001', 'Freight', 'Export ocean freight', 1650, 'USD', 34, 'BlueWave Freight Services', 'Paid', 'DEMO-PAY-003'),
            ('DEMO-IMP-002', 'Customs Duty', 'Import customs duty', 385000, 'INR', 1, 'Government Customs', 'Pending', ''),
            ('DEMO-EXP-002', 'Freight', 'Estimated export freight', 980, 'USD', 0, 'BlueWave Freight Services', 'Pending', ''),
        ]
        for reference, category, description, amount, currency, days_ago, vendor, status, payment_reference in expense_rows:
            shipment_id = shipment_ids[reference]
            exists = db.execute(
                'SELECT 1 FROM expenses WHERE shipment_id = ? AND description = ?',
                (shipment_id, description)
            ).fetchone()
            if not exists:
                db.execute(
                    '''INSERT INTO expenses
                       (shipment_id, category, description, amount, currency, expense_date, vendor, payment_status, payment_reference)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (shipment_id, category, description, amount, currency,
                     (today - timedelta(days=days_ago)).isoformat(), vendor, status, payment_reference or None)
                )

        db.commit()
        click.echo('Demo data inserted or existing demo records completed.')


if __name__ == '__main__':
    if len(__import__('sys').argv) > 1 and __import__('sys').argv[1] in {'create-admin', 'init-db', 'seed-demo'}:
        app.cli.main(args=__import__('sys').argv[1:])
    else:
        app.run(host='127.0.0.1', port=5000, debug=False)
