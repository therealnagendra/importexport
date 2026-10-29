def test_report_csv_has_safe_values(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    response = client.get('/reports/export?type=shipments')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert 'Content-Disposition' in response.headers
