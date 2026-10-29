import io


def test_upload_rejected_for_invalid_extension(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    response = client.post('/documents/upload', data={
        'csrf_token': 'test-token',
        'reference_no': 'DOC-1',
        'document_type': 'Commercial Invoice',
        'file': (io.BytesIO(b'not an image'), 'bad.txt')
    }, follow_redirects=True)
    assert b'Only PDF, JPG, JPEG and PNG files are allowed' in response.data
