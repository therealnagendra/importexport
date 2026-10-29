import csv
import io
import secrets
import uuid
from pathlib import Path

from flask import Response, current_app
from werkzeug.utils import secure_filename


def generate_reference(prefix):
    return f'{prefix}-{uuid.uuid4().hex[:8].upper()}'


def random_token():
    return secrets.token_hex(16)


def is_allowed_document_extension(filename):
    return Path(filename).suffix.lower() in {'.pdf', '.jpg', '.jpeg', '.png'}


def secure_upload_path(filename):
    safe = secure_filename(filename)
    if not safe:
        raise ValueError('The uploaded file is missing a valid name.')
    return Path(current_app.config['UPLOAD_FOLDER']) / f'{uuid.uuid4().hex}_{safe}'


def sanitize_csv_value(value):
    if value is None:
        return ''
    text = str(value)
    if text.startswith(('=', '+', '-', '@')):
        text = "'" + text
    return text


def export_csv_response(rows, fieldnames, filename):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows({k: sanitize_csv_value(row.get(k, '')) for k in fieldnames} for row in rows)
    return Response(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
