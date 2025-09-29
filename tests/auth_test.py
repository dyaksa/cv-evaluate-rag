def test_register(client, mock_register_usecase):
    mock_register_usecase.return_value = True
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'securepassword'
    })
    assert response.status_code == 201
    assert response.get_json() == {'message': 'User registered successfully'}
    mock_register_usecase.assert_called_once_with(email='test@example.com', password='securepassword')

def test_login(client, mock_login_usecase):
    mock_login_usecase.return_value = 'mocked_jwt_token'
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'securepassword'
    })
    assert response.status_code == 200
    assert response.get_json() == {'access_token': 'mocked_jwt_token'}
    mock_login_usecase.assert_called_once_with(email='test@example.com', password='securepassword')