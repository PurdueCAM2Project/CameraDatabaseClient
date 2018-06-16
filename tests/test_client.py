import unittest
import sys
import mock
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from pythonAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera
from pythonAPIClient.client import Client
from pythonAPIClient.error import AuthenticationError, InternalError, InvalidClientIdError, InvalidClientSecretError , ResourceNotFoundError , FormatError


class TestClient(unittest.TestCase):

    def setUp(self):
        self.base_URL = 'https://cam2-api.herokuapp.com/'
        pass

    def test_client_init_wrong_ClientId_Length(self):
        with self.assertRaises(InvalidClientIdError):
            client = Client('dummyID', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')

    def test_client_init_wrong_Client_Secret_Length(self):
        with self.assertRaises(InvalidClientSecretError):
            client = Client(
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                'dummySecret')

    def test_client_init(self):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.id, clientId, 'ID not stored in the client object.')
        self.assertEqual(client.secret, clientSecret, 'Secret not stored in the client object.')
        self.assertIs(client.token, None, 'Token not set to default')

    def test_build_header(self):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'dummy'
        head_example = {'Authorization': 'Bearer ' + 'dummy'}
        self.assertEqual(client.header_builder(), head_example)

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self, mock_get, mock_http_error_handler):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_Secret(self, mock_get, mock_http_error_handler):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_all_correct_Internal_error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        expected_dict = {
            "token": "correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search?country=USA'
        with self.assertRaises(KeyError):
            client.search_camera(country='USA')
        mock_get.assert_called_with(url,headers={'Authorization': 'Bearer correctToken'})
        self.assertEqual(2, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Expired_Token(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search?country=USA'
        with self.assertRaises(TypeError):
            client.search_camera(country='USA')
        mock_get.assert_called_with(self.base_URL +'auth/?clientID='+clientId+'&clientSecret='+clientSecret)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Internal_Error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
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

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register(self, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "clientID": "test_clientID",
            "clientSecret": "test_clientSecret"
        }
        mock_post.return_value = mock_response
        # validate result
        expected_clientID = 'test_clientID'
        expected_clientSecret = 'test_clientSecret'
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer correctToken'}

        clientID, clientSecret = client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header)
        self.assertEqual(clientID, expected_clientID)
        self.assertEqual(clientSecret, expected_clientSecret)
        self.assertEqual(2, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_incorrect_token(self, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Failed to authenticate token"
        }
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer None'}
        with self.assertRaises(ResourceNotFoundError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_register_expired_token(self, mock_get, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        # set request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired"
        }
        mock_post.return_value = mock_response
        with self.assertRaises(InternalError):
            client.register('testowner')
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer ExpiredToken'}
        mock_post.assert_called_once_with(url, headers=header)
        mock_get.assert_called_with(self.base_URL +'auth/?clientID='+clientId+'&clientSecret='+clientSecret)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_no_owner(self, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Must include the owner's username"
        }
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(FormatError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_incorrect_clientID(self, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "No app exists with given clientID"
        }
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(ResourceNotFoundError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_internal_error(self, mock_post):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register/?owner=testowner&permissionLevel=user'
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(InternalError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 200
        clientObject = [
            {'clientID': 'test_clientID1'},
            {'clientID': 'test_clientID2'}]
        mock_response.json.return_value = clientObject

        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/by-owner?owner=test'
        expected_clientID_array = ['test_clientID1', 'test_clientID2']
        self.assertEqual(client.client_ids_by_owner("test"), expected_clientID_array)
        mock_get.assert_called_once_with(url)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_no_token(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Failed to authenticate token'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(AuthenticationError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_with(self.base_URL +'auth/?clientID='+clientId+'&clientSecret='+clientSecret)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_expired_token(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(AuthenticationError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_with(self.base_URL +'auth/?clientID='+clientId+'&clientSecret='+clientSecret)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_incorrect_clientID(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given clientID'
        }
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/by-owner?owner=testowner'
        with self.assertRaises(ResourceNotFoundError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_once_with(url)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_internal_error(self, mock_get):
        clientId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        clientSecret = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        client = Client(clientId, clientSecret)
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/by-owner?owner=testowner'
        with self.assertRaises(InternalError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_once_with(url)
        self.assertEqual(0, mock_response.json.call_count)

if __name__ == '__main__':
    unittest.main()
