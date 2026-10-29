import sqlite3

from flask import g, current_app


def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS application_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
        full_name TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS parties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        party_type TEXT NOT NULL,
        contact_person TEXT,
        email TEXT,
        telephone TEXT,
        address TEXT,
        country TEXT,
        tax_id TEXT,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        agent_type TEXT NOT NULL,
        contact_person TEXT,
        email TEXT,
        telephone TEXT,
        office_address TEXT,
        country TEXT,
        license_reference TEXT,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT NOT NULL UNIQUE,
        shipment_type TEXT NOT NULL CHECK(shipment_type IN ('Import', 'Export')),
        product_description TEXT NOT NULL,
        importer_id INTEGER,
        exporter_id INTEGER,
        origin_country TEXT,
        destination_country TEXT,
        origin_port TEXT,
        destination_port TEXT,
        hs_code TEXT,
        quantity REAL,
        unit TEXT,
        invoice_value REAL,
        currency TEXT,
        exchange_rate REAL,
        invoice_no TEXT,
        invoice_date TEXT,
        shipment_date TEXT,
        expected_arrival TEXT,
        actual_arrival TEXT,
        container_no TEXT,
        bl_awb_no TEXT,
        transport_mode TEXT,
        carrier TEXT,
        agent_id INTEGER,
        assigned_staff TEXT,
        shipment_status TEXT NOT NULL DEFAULT 'Pending',
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (importer_id) REFERENCES parties(id),
        FOREIGN KEY (exporter_id) REFERENCES parties(id),
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS tracking_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id INTEGER NOT NULL,
        milestone TEXT NOT NULL,
        milestone_date TEXT NOT NULL,
        location TEXT,
        status TEXT,
        remarks TEXT,
        user_id INTEGER,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT NOT NULL UNIQUE,
        shipment_id INTEGER,
        document_type TEXT NOT NULL,
        issue_date TEXT,
        expiry_date TEXT,
        description TEXT,
        original_name TEXT,
        stored_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        uploaded_by INTEGER,
        uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE SET NULL,
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        expense_date TEXT NOT NULL,
        vendor TEXT,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        payment_reference TEXT,
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_shipments_type ON shipments(shipment_type);
    CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(shipment_status);
    CREATE INDEX IF NOT EXISTS idx_shipments_dates ON shipments(shipment_date, expected_arrival);
    CREATE INDEX IF NOT EXISTS idx_parties_type ON parties(party_type);
    CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
    CREATE INDEX IF NOT EXISTS idx_documents_shipment ON documents(shipment_id);
    CREATE INDEX IF NOT EXISTS idx_expenses_shipment ON expenses(shipment_id);
    CREATE INDEX IF NOT EXISTS idx_tracking_shipment ON tracking_milestones(shipment_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_application_settings_key ON application_settings(key);
    ''')

    app_settings = db.execute('SELECT value FROM application_settings WHERE key = ?', ('schema_version',)).fetchone()
    if app_settings is None:
        db.execute('INSERT INTO application_settings (key, value) VALUES (?, ?)', ('schema_version', '1'))
        db.commit()
