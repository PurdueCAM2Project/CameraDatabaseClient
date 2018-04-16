import unittest
import sys
import mock
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from pythonAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera
from pythonAPIClient.client import Client
from pythonAPIClient.error import AuthenticationError, InternalError


class TestClient(unittest.TestCase):

    def setUp(self):
        self.base_URL = 'https://cam2-api.herokuapp.com/'
        pass

    def test_client_init(self):
        client = Client('dummyID', 'dummySecret')
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.id, 'dummyID', 'ID not stored in the client object.')
        self.assertEqual(client.secret, 'dummySecret', 'Secret not stored in the client object.')
        self.assertIs(client.token, None, 'Token not set to default')

    def test_build_header(self):
        client = Client('dummyID', 'dummySecret')
        client.token = 'dummy'
        head_example = {'Authorization': 'Bearer ' + 'dummy'}
        self.assertEqual(client.header_builder(), head_example)

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self, mock_get,  mock_http_error_handler):
        client = Client('dummyID', 'dummySecret')
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        url = self.base_URL + 'auth/?clientID=dummyID&clientSecret=dummySecret'
        with self.assertRaises(AuthenticationError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_Secret(self, mock_get,  mock_http_error_handler):
        client = Client('correctID', 'dummySecret')
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        url = self.base_URL + 'auth/?clientID=correctID&clientSecret=dummySecret'
        with self.assertRaises(AuthenticationError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct(self, mock_get):
        client = Client('correctID', 'correctSecret')
        mock_response = mock.Mock()
        expected_dict = {
            "token":"correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_dict = client.request_token()
        mock_get.assert_called_once_with(
            self.base_URL+'auth/?clientID=correctID&clientSecret=correctSecret')
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(client.token, 'correctToken', 'token not stored in the client object.')

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct_Internal_error(self, mock_get):
        client = client = Client('correctID', 'correctSecret')
        mock_response = mock.Mock()
        mock_response.status_code = 501
        mock_get.return_value = mock_response
        url = self.base_URL + 'auth/?clientID=correctID&clientSecret=correctSecret'
        with self.assertRaises(InternalError):
            client.request_token()
        mock_get.assert_called_once_with(url)
        self.assertEqual(0, mock_response.json.call_count)

if __name__ == '__main__':
    unittest.main()
