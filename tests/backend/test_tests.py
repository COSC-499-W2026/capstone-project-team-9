def test_mock_api_client(mock_api_client):
    users = mock_api_client.get_users()
    assert users[0]["name"] == "Alice"
    mock_api_client.get_users.assert_called_once()
"juat a fake test to makes sure everthing is working, will delete when actual tests are written"