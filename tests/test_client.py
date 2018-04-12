import unittest
import sys
import mock
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from pythonAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera
from pythonAPIClient.client import Client
from pythonAPIClient.error import Error


class TestClient(unittest.TestCase):

    def setUp(self):
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

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self,mock_get):
        client = Client('dummyID', 'dummySecret')
        mock_response = mock.Mock()
        expected_dict = {
            "errorType": "ResourceNotFoundError",
            "message": "No app exists with given clientID."
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        response_dict = client.request_token()
        mock_get.assert_called_once_with('https://cam2-api.herokuapp.com/auth/?clientID=dummyID&clientSecret'
                                         '=dummySecret')
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(response_dict, '404-No app exists with given clientID.', 'The response handling for '
                                                                                  'incorrect credentials is incorrect')

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_Secret(self, mock_get):
        client = Client('correctID', 'dummySecret')
        mock_response = mock.Mock()
        expected_dict = {
            "errorType":"AuthenticationError",
            "message":"Bad client secret."
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        response_dict = client.request_token()
        mock_get.assert_called_once_with(
            'https://cam2-api.herokuapp.com/auth/?clientID=dummyID&clientSecret=dummySecret')
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(response_dict, '404-Bad client secret.', 'The response handling for incorrect secret is incorrect')

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct(self, mock_get):
        client = Client('correctID', 'correctSecret')
        mock_response = mock.Mock()
        expected_dict = {
            "token":"correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        response_dict = client.request_token()
        mock_get.assert_called_once_with(
            'https://cam2-api.herokuapp.com/auth/?clientID=dummyID&clientSecret=dummySecret')
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(response_dict, 'OK', 'The response handling for correct credentials is incorrect')
        self.assertEqual(client.token, 'correctToken', 'token not stored in the client object.')


if __name__ == '__main__':
    unittest.main()
