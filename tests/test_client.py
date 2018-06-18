"""
fix me
"""
import unittest
import sys
from os import path
import mock
from pythonAPIClient.client import Client
from pythonAPIClient.error import AuthenticationError, InternalError, InvalidClientIdError,\
     InvalidClientSecretError, ResourceNotFoundError, FormatError
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class TestClient(unittest.TestCase):

    def setUp(self):
        self.base_URL = 'https://cam2-api.herokuapp.com/'

    def test_client_init_wrong_ClientId_Length(self):
        with self.assertRaises(InvalidClientIdError):
            client = Client('dummyID', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
                                       'bbbbbbbbbbbbbbbbbbbbbbb')
            return client

    def test_client_init_wrong_Client_Secret_Length(self):
        with self.assertRaises(InvalidClientSecretError):
            client = Client(
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                'aaaaaaaaaaaaaaaaaaaaaa',
                'dummySecret')
            return client

    def test_client_init(self):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' \
                       'bbbbbbb'
        client = Client(clientId, clientSecret)
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.clientId, clientId, 'ID not stored in the client object.')
        self.assertEqual(client.clientSecret, clientSecret, 'Secret not stored in the client '
                                                            'object.')
        self.assertIs(client.token, None, 'Token not set to default')

    def test_build_header(self):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' \
                       'bbbb'
        client = Client(clientId, clientSecret)
        client.token = 'dummy'
        head_example = {'Authorization': 'Bearer ' + 'dummy'}
        self.assertEqual(client.header_builder(), head_example)

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self, mock_get, mock_http_error_handler):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Cannot find client with that ClientID"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        url = self.base_URL + 'auth/?clientID='+clientId+'&clientSecret='+clientSecret
        with self.assertRaises(ResourceNotFoundError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(1, mock_response.json.call_count)
        return mock_http_error_handler

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_Secret(self, mock_get, mock_http_error_handler):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Bad client secret"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        url = self.base_URL + 'auth/?clientID='+clientId+'&clientSecret='+clientSecret
        with self.assertRaises(AuthenticationError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(1, mock_response.json.call_count)
        return mock_http_error_handler

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        expected_dict = {
            "token": "correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_dict = client.request_token()
        mock_get.assert_called_once_with(
            self.base_URL + 'auth/?clientID='+clientId+'&clientSecret='+clientSecret)
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(client.token, 'correctToken', 'token not stored in the client object.')
        return response_dict

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct_Internal_error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = self.base_URL +'auth/?clientID='+clientId+'&clientSecret='+clientSecret
        with self.assertRaises(InternalError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_no_token(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        expected_dict = {
            "token": "correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search?country=USA'
        with self.assertRaises(TypeError):
            client.search_camera(country='USA')
        mock_get.assert_called_with(url, headers={'Authorization': 'Bearer correctToken'})
        self.assertEqual(2, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Expired_Token(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        with self.assertRaises(TypeError):
            client.search_camera(country='USA')
        mock_get.assert_called_with(self.base_URL + 'auth/?clientID=' + clientId +
                                    '&clientSecret=' + clientSecret)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Internal_Error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'CorrectToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search?country=USA'
        with self.assertRaises(InternalError):
            client.search_camera(country='USA')
        mock_get.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'})
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Format_Error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
                   'aaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'CorrectToken'
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 422
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search?country=USA'
        with self.assertRaises(FormatError):
            client.search_camera(country='USA')
        mock_get.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'})
        self.assertEqual(1, mock_response.json.call_count)


if __name__ == '__main__':
    unittest.main()
