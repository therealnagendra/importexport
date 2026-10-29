from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_file, session

from app.db import get_db
from app.decorators import csrf_required, login_required
from app.utils import generate_reference, is_allowed_document_extension, secure_upload_path

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/documents')
@login_required
def list_documents():
    db = get_db()
    rows = db.execute('''
        SELECT d.*, s.reference_no AS shipment_reference, u.username AS uploaded_by_name
        FROM documents d
        LEFT JOIN shipments s ON s.id = d.shipment_id
        LEFT JOIN users u ON u.id = d.uploaded_by
        ORDER BY d.uploaded_at DESC
    ''').fetchall()
    return render_template('documents/list.html', rows=rows)


@documents_bp.route('/documents/upload', methods=['GET', 'POST'])
@login_required
@csrf_required
def upload_document():
    db = get_db()
    if request.method == 'GET':
        shipments = db.execute('SELECT id, reference_no FROM shipments ORDER BY reference_no').fetchall()
        return render_template('documents/form.html', shipments=shipments)

    reference_no = request.form.get('reference_no', '').strip() or generate_reference('DOC')
    shipment_id = request.form.get('shipment_id') or None
    document_type = request.form.get('document_type', 'Other')
    issue_date = request.form.get('issue_date') or None
    expiry_date = request.form.get('expiry_date') or None
    description = request.form.get('description', '')
    uploaded_file = request.files.get('file')

    if not uploaded_file or not uploaded_file.filename:
        flash('Please select a file to upload.', 'error')
        return redirect('/documents/upload')

    if not is_allowed_document_extension(uploaded_file.filename):
        flash('Only PDF, JPG, JPEG and PNG files are allowed.', 'error')
        return redirect('/documents/upload')

    try:
        destination = secure_upload_path(uploaded_file.filename)
        uploaded_file.save(destination)

        db.execute('''
            INSERT INTO documents (
                reference_no, shipment_id, document_type, issue_date, expiry_date,
                description, original_name, stored_filename, file_path, uploaded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reference_no, shipment_id, document_type, issue_date, expiry_date,
            description, uploaded_file.filename, destination.name, str(destination), session.get('user_id')
        ))
        db.commit()
        flash('Document uploaded successfully.', 'success')
        return redirect('/documents')
    except Exception as exc:
        flash(f'Upload failed: {exc}', 'error')
        return redirect('/documents/upload')


@documents_bp.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    db = get_db()
    row = db.execute('SELECT * FROM documents WHERE id = ?', (document_id,)).fetchone()
    if not row or not Path(row['file_path']).exists():
        flash('Document file not found.', 'error')
        return redirect('/documents')
    return send_file(row['file_path'], as_attachment=True, download_name=row['original_name'])


@documents_bp.route('/documents/<int:document_id>/delete', methods=['POST'])
@login_required
@csrf_required
def delete_document(document_id):
    db = get_db()
    row = db.execute('SELECT * FROM documents WHERE id = ?', (document_id,)).fetchone()
    if row:
        try:
            Path(row['file_path']).unlink(missing_ok=True)
        except Exception:
            pass
        db.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        db.commit()
        flash('Document deleted.', 'success')
    return redirect('/documents')
