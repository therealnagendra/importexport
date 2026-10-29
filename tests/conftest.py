import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db, init_db


@pytest.fixture()
def client():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        upload_folder = os.path.join(tmpdir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        app = create_app({
            'TESTING': True,
            'DATABASE_PATH': db_path,
            'UPLOAD_FOLDER': upload_folder,
            'SECRET_KEY': 'test-secret'
        })
        with app.app_context():
            init_db()
            db = get_db()
            db.execute('INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)',
                       ('admin', generate_password_hash('admin123'), 'admin', 'Admin User'))
            db.commit()
        with app.test_client() as client:
            yield client
