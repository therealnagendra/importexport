def test_shipments_create_and_filter(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    response = client.post('/shipments/new', data={
        'csrf_token': 'test-token',
        'reference_no': 'IMP-001',
        'shipment_type': 'Import',
        'product_description': 'Rice cargo',
        'origin_country': 'India',
        'destination_country': 'UAE',
        'carrier': 'Blue Ocean',
        'shipment_status': 'Pending'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'IMP-001' in response.data
