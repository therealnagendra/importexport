def test_login_success(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_login_failure(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'wrong'}, follow_redirects=True)
    assert b'Invalid credentials' in response.data


def test_unauthorized_access(client):
    response = client.get('/shipments', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
