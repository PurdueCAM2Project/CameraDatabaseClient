"""
fix me
"""
import unittest
import sys
from os import path
import mock
from pythonAPIClient.client import Client
from pythonAPIClient.error import AuthenticationError, InternalError, InvalidClientIdError,\
     InvalidClientSecretError, ResourceNotFoundError, FormatError, AuthorizationError
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

class TestClient(unittest.TestCase):

    def setUp(self):
        self.base_URL = 'https://cam2-api.herokuapp.com/'

    def test_client_init_wrong_ClientId_Length(self):
        with self.assertRaises(InvalidClientIdError):
            client = Client('dummyID', '0' * 71)
            return client

    def test_client_init_wrong_Client_Secret_Length(self):

        # client secret shorter than 71
        with self.assertRaises(InvalidClientSecretError):
            client = Client('0' * 96, 'dummySecret')
            return client

    def test_client_init(self):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.clientId, clientId, 'ID not stored in the client object.')
        self.assertEqual(client.clientSecret, clientSecret,
                         'Secret not stored in the client object.')
        self.assertIs(client.token, None, 'Token not set to default')

        #client secret longer than 71
        clientSecret2 = '0' * 80
        client2 = Client(clientId, clientSecret2)
        self.assertTrue(isinstance(client2, Client))
        self.assertEqual(client2.clientId, clientId, 'ID not stored in the client object.')
        self.assertEqual(client2.clientSecret, clientSecret2,
                         'Secret not stored in the client object.')
        self.assertIs(client2.token, None, 'Token not set to default')

    def test_build_header(self):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'dummy'
        head_example = {'Authorization': 'Bearer ' + 'dummy'}
        self.assertEqual(client.header_builder(), head_example)

    @mock.patch('pythonAPIClient.error.AuthenticationError')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self, mock_get, mock_http_error_handler):
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        # set result for request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.json.return_value = []

        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        camera = client.search_camera(country='USA')
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual([], camera)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Internal_Error(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        url = Client.base_URL + 'apps/register'
        header = {'Authorization': 'Bearer correctToken'}
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        resultID, resultSecret = client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_clientID)
        self.assertEqual(resultSecret, expected_clientSecret)
        self.assertEqual(2, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_register_expired_token_success(self, mock_get, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired',
        }
        # set second request.post's result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'clientID': 'test_clientID',
            'clientSecret': 'test_clientSecret'
        }
        mock_post.side_effect = [mock_response, mock_response2]
        # set request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'newToken'
        }
        mock_get.return_value = mock_get_response
        # run the test
        resultID, resultSecret = client.register('testowner')
        self.assertEqual(resultID, 'test_clientID')
        self.assertEqual(resultSecret, 'test_clientSecret')
        mock_get.assert_called_with(self.base_URL +'auth/?clientID='+clientId+
                                    '&clientSecret='+clientSecret)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        call_list = [mock.call(self.base_URL + 'apps/register', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/register', headers=newheaders, data=data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.post')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_register_expired_token_failure(self, mock_get, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired',
        }
        mock_post.return_value = mock_response
        # set request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'newToken'
        }
        mock_get.return_value = mock_get_response
        # run the test
        with self.assertRaises(AuthenticationError):
            client.register('testowner')
        mock_get.assert_called_with(self.base_URL + 'auth/?clientID=' + clientId +
                                    '&clientSecret=' + clientSecret)
        self.assertEqual(3, mock_post.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        call_list = [mock.call(self.base_URL + 'apps/register', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/register', headers=newheaders, data=data),
                     mock.call(self.base_URL + 'apps/register', headers=newheaders, data=data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_no_owner(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        # set request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Must include the owner's username"
        }
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register'
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        header = {'Authorization': 'Bearer correctToken'}
        with self.assertRaises(FormatError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_incorrect_clientID(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        url = Client.base_URL + 'apps/register'
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(ResourceNotFoundError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_register_internal_error(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        # validate result
        url = Client.base_URL + 'apps/register'
        data = {'owner': 'testowner', 'permissionLevel': 'user'}
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(InternalError):
            client.register('testowner')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_all_correct(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        clientObject = [
            {'clientID': 'test_clientID1'},
            {'clientID': 'test_clientID2'}]
        mock_response.json.return_value = clientObject

        mock_get.return_value = mock_response
        headers = {'Authorization': 'Bearer correctToken'}
        url = Client.base_URL + 'apps/by-owner'
        param = {'owner': 'testowner'}
        expected_clientID_array = ['test_clientID1', 'test_clientID2']
        self.assertEqual(client.client_ids_by_owner("testowner"), expected_clientID_array)
        mock_get.assert_called_once_with(url, headers=headers, params=param)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_expired_token_success(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        # set first requests.get's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired',
        }
        # set request_token()'s result
        mock_response1 = mock.Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'token': 'newToken'
        }
        # set second requests.get's result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [
            {'clientID': 'test_clientID1'},
            {'clientID': 'test_clientID2'}
        ]
        mock_get.side_effect = [mock_response, mock_response1, mock_response2]
        # run the test
        client.client_ids_by_owner('testowner')
        self.assertEqual(3, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        params = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/by-owner', headers=headers, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/by-owner', headers=newheaders, params=params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_expired_token_failure(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        # set first requests.get's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired',
        }
        # set request_token()'s result
        mock_response1 = mock.Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'token': 'newToken'
        }
        mock_get.side_effect = [mock_response, mock_response1, mock_response,
                                mock_response1, mock_response, mock_response1, mock_response]
        # run the test
        with self.assertRaises(AuthenticationError):
            client.client_ids_by_owner('testowner')
        self.assertEqual(5, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        params = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/by-owner', headers=headers, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/by-owner', headers=newheaders, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/by-owner', headers=newheaders, params=params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_incorrect_clientID(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given clientID'
        }
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/by-owner'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        with self.assertRaises(ResourceNotFoundError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_once_with(url, headers=headers, params=param)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_clientID_by_owner_internal_error(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/by-owner'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        with self.assertRaises(InternalError):
            client.client_ids_by_owner('testowner')
        mock_get.assert_called_once_with(url, headers=headers, params=param)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_clientID_all_correct(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'api_usage': 7
        }
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/1/usage'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        self.assertEqual(client.usage_by_client('1', 'testowner'), 7)
        mock_get.assert_called_once_with(url, headers=headers, params=param)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_client_expired_token_success(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_response1 = mock.Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'token': 'newToken'
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'api_usage': 1
        }
        mock_get.side_effect = [mock_response, mock_response1, mock_response2]
        self.assertEqual(1, client.usage_by_client('1', 'testowner'))
        self.assertEqual(3, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        params = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/1/usage', headers=headers, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/1/usage', headers=newheaders, params=params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_client_expired_token_failure(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken'
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response, mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            client.usage_by_client('1', 'testowner')
        self.assertEqual(5, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        params = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/1/usage', headers=headers, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/1/usage', headers=newheaders, params=params),
                     mock.call(self.base_URL + 'auth/?clientID=' + clientId +
                               '&clientSecret=' + clientSecret),
                     mock.call(self.base_URL + 'apps/1/usage', headers=newheaders, params=params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_client_authorization_error(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'message': 'Forbidden to view API usage of this client'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(AuthorizationError):
            client.usage_by_client('1', 'testowner')
        url = Client.base_URL + 'apps/1/usage'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        mock_get.assert_called_once_with(url, headers=headers, params=param)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_client_id_not_found(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given clientID'
        }
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/1/usage'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        with self.assertRaises(ResourceNotFoundError):
            client.usage_by_client('1', 'testowner')
        mock_get.assert_called_once_with(url, headers=headers, params=param)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_get_usage_by_client_internal_error(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = Client.base_URL + 'apps/1/usage'
        param = {'owner': 'testowner'}
        headers = {'Authorization': 'Bearer correctToken'}
        with self.assertRaises(InternalError):
            client.usage_by_client('1', 'testowner')
        mock_get.assert_called_once_with(url, headers=headers, params=param)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_owner(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'OK'
        }
        mock_put.return_value = mock_response
        url = Client.base_URL + 'apps/1'
        headers = {'Authorization': 'Bearer correctToken'}
        data = {'owner': 'testowner'}
        self.assertEqual(client.update_owner('1', 'testowner'), 'OK')
        mock_put.assert_called_once_with(url, headers=headers, data=data)

    @mock.patch('pythonAPIClient.client.requests.put')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_update_owner_expired_token_success(self, mock_get, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = {
            'message': 'OK'
        }
        mock_put.side_effect = [mock_response, mock_response3]

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken'
        }
        mock_get.return_value = mock_response2
        self.assertEqual('OK', client.update_owner('1', 'testowner'))
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/1', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.put')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_update_owner_expired_token_failure(self, mock_get, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_put.return_value = mock_response

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken',
        }
        mock_get.return_value = mock_response2
        with self.assertRaises(AuthenticationError):
            client.update_owner('1', 'testowner')
        self.assertEqual(3, mock_put.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'owner': 'testowner'}
        call_list = [mock.call(self.base_URL + 'apps/1', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_owner_invalid_clientid(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given client id.'
        }
        mock_put.return_value = mock_response
        url = Client.base_URL + 'apps/1'
        headers = {'Authorization': 'Bearer correctToken'}
        data = {'owner': 'testowner'}
        with self.assertRaises(ResourceNotFoundError):
            client.update_owner('1', 'testowner')
        mock_put.assert_called_once_with(url, headers=headers, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_permissionLevel(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'OK'
        }
        mock_put.return_value = mock_response
        headers = {'Authorization': 'Bearer correctToken'}
        url = Client.base_URL + 'apps/1'
        data = {'permissionLevel': 'user'}
        self.assertEqual(client.update_permission('1', 'user'), 'OK')
        mock_put.assert_called_once_with(url, headers=headers, data=data)

    @mock.patch('pythonAPIClient.client.requests.put')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_update_permissionLevel_expired_token_success(self, mock_get, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = {
            'message': 'OK'
        }
        mock_put.side_effect = [mock_response, mock_response3]

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken',
        }
        mock_get.return_value = mock_response2
        self.assertEqual(client.update_permission('1', 'user'), 'OK')
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'permissionLevel': 'user'}
        call_list = [mock.call(self.base_URL + 'apps/1', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.put')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_update_permissionLevel_expired_token_failure(self, mock_get, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        mock_put.return_value = mock_response

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'newToken',
        }
        mock_get.return_value = mock_response2
        with self.assertRaises(AuthenticationError):
            client.update_permission('1', 'user')
        self.assertEqual(3, mock_put.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'permissionLevel': 'user'}
        call_list = [mock.call(self.base_URL + 'apps/1', headers=headers, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data),
                     mock.call(self.base_URL + 'apps/1', headers=newheaders, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_ip(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "5ae0ecbd336359291be74c12"
        }

        mock_put.return_value = mock_response
        # validate result
        expected_cameraID = '5ae0ecbd336359291be74c12'
        url = Client.base_URL + 'cameras/' + expected_cameraID
        header = {'Authorization': 'Bearer correctToken'}
        data = {'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'cameraID': '5ae0ecbd336359291be74c12', 'type': 'ip',
                'retrieval': '{"ip": null, "port": "8080", "brand": "test_brand", "model": "test_model", '
                             '"image_path": "test_image_path", "video_path": "test_vid_path"}'}

        resultID = client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='ip',
                                        is_active_image=False, is_active_video=True, legacy_cameraID=000000000,
                                        source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                        state='Indiana', city='West Lafayette', resolution_width=720,
                                        resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                        timezone_name='test_t_name', reference_logo='test_ref_logo',
                                        reference_url='test_ref_url', port='8080', brand='test_brand',
                                        model='test_model', image_path='test_image_path', video_path='test_vid_path')
        mock_put.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_non_ip(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "5ae0ecbd336359291be74c12"
        }
        mock_put.return_value = mock_response
        # validate result
        expected_cameraID = '5ae0ecbd336359291be74c12'
        url = Client.base_URL + 'cameras/' + expected_cameraID
        header = {'Authorization': 'Bearer correctToken'}
        data = {'video_path': None, 'image_path': None, 'model': None, 'brand': None, 'port': None,
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None, 'ip': None,
                'is_active_video': True, 'is_active_image': False, 'cameraID': '5ae0ecbd336359291be74c12',
                'type': 'non-ip', 'retrieval': '{"snapshot_url": "test_snapshot"}'}

        resultID = client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='non-ip',
                                        is_active_image=False, is_active_video=True, snapshot_url='test_snapshot',
                                        m3u8_url=None, legacy_cameraID=000000000, source='test_source',
                                        latitude='test_lad', longitude='test_long', country='USA', state='Indiana',
                                        city='West Lafayette', resolution_width=720, resolution_height=480,
                                        utc_offset=3, timezone_id='test_t_id', timezone_name='test_t_name',
                                        reference_logo='test_ref_logo', reference_url='test_ref_url')
        mock_put.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_stream(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "5ae0ecbd336359291be74c12"
        }
        mock_put.return_value = mock_response
        # validate result
        expected_cameraID = '5ae0ecbd336359291be74c12'
        url = Client.base_URL + 'cameras/' + expected_cameraID
        header = {'Authorization': 'Bearer correctToken'}
        data = {'video_path': None, 'image_path': None, 'model': None, 'brand': None, 'port': None,
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'snapshot_url': None, 'ip': None,
                'is_active_video': True, 'is_active_image': False, 'cameraID': '5ae0ecbd336359291be74c12',
                'type': 'stream', 'retrieval': '{"m3u8_url": "test_m3u8"}'}

        resultID = client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='stream',
                                        is_active_image=False, is_active_video=True, snapshot_url=None,
                                        m3u8_url='test_m3u8', legacy_cameraID=000000000, source='test_source',
                                        latitude='test_lad', longitude='test_long', country='USA', state='Indiana',
                                        city='West Lafayette', resolution_width=720, resolution_height=480,
                                        utc_offset=3, timezone_id='test_t_id', timezone_name='test_t_name',
                                        reference_logo='test_ref_logo', reference_url='test_ref_url')
        mock_put.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_update_camera_expired_token_success(self, mock_get, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired'
        }
        # set second request.post's result
        testCamID = '5ae0ecbd336359291be74c12'
        mock_response2 = mock.Mock()
        mock_response2.status_code = 201
        mock_response2.json.return_value = {
            'cameraID': '5ae0ecbd336359291be74c12'
        }
        mock_put.side_effect = [mock_response, mock_response2]
        # set request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'newToken'
        }
        mock_get.return_value = mock_get_response
        # run the test
        resultID = client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='ip',
                                        is_active_image=False, is_active_video=True, legacy_cameraID=000000000,
                                        source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                        state='Indiana', city='West Lafayette', resolution_width=720,
                                        resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                        timezone_name='test_t_name', reference_logo='test_ref_logo',
                                        reference_url='test_ref_url', port='8080', brand='test_brand',
                                        model='test_model', image_path='test_image_path', video_path='test_vid_path')
        self.assertEqual(resultID, testCamID)
        mock_get.assert_called_with(self.base_URL + 'auth/?clientID=' + clientId +
                                    '&clientSecret=' + clientSecret)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}

        data = {'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'cameraID': '5ae0ecbd336359291be74c12', 'type': 'ip',
                'retrieval': '{"ip": null, "port": "8080", "brand": "test_brand", "model": "test_model", '
                             '"image_path": "test_image_path", "video_path": "test_vid_path"}'}
        call_list = [mock.call(self.base_URL + 'cameras/' + testCamID, headers=headers, data=data),
                     mock.call(self.base_URL + 'cameras/' + testCamID, headers=newheaders, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_internal_error(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_put.return_value = mock_response
        # validate result
        testCamID = '5ae0ecbd336359291be74c12'
        url = Client.base_URL + 'cameras/' + testCamID
        data = {'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'cameraID': '5ae0ecbd336359291be74c12', 'type': 'ip',
                'retrieval': '{"ip": null, "port": "8080", "brand": "test_brand", "model": "test_model", '
                             '"image_path": "test_image_path", "video_path": "test_vid_path"}'}
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(InternalError):
            client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='ip',
                                 is_active_image=False, is_active_video=True, legacy_cameraID=000000000,
                                 source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                 state='Indiana', city='West Lafayette', resolution_width=720,
                                 resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                 timezone_name='test_t_name', reference_logo='test_ref_logo',
                                 reference_url='test_ref_url', port='8080', brand='test_brand',
                                 model='test_model', image_path='test_image_path', video_path='test_vid_path')
        mock_put.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_all_correct_Format_Error(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'CorrectToken'
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 422
        mock_put.return_value = mock_response
        testCamID = '5ae0ecbd336359291be74c12'
        url = self.base_URL + 'cameras/' + testCamID
        data = {'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'cameraID': '5ae0ecbd336359291be74c12', 'type': 'ip',
                'retrieval': '{"ip": null, "port": "8080", "brand": "test_brand", "model": "test_model", '
                             '"image_path": "test_image_path", "video_path": "test_vid_path"}'}
        with self.assertRaises(FormatError):
            client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='ip',
                                 is_active_image=False, is_active_video=True, legacy_cameraID=000000000,
                                 source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                 state='Indiana', city='West Lafayette', resolution_width=720,
                                 resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                 timezone_name='test_t_name', reference_logo='test_ref_logo',
                                 reference_url='test_ref_url', port='8080', brand='test_brand',
                                 model='test_model', image_path='test_image_path', video_path='test_vid_path')
        mock_put.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'}, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.put')
    def test_update_camera_invalid_clientID(self, mock_put):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given client id.'
        }
        mock_put.return_value = mock_response
        testCamID = '5ae0ecbd336359291be74c12'
        url = self.base_URL + 'cameras/' + testCamID
        headers = {'Authorization': 'Bearer correctToken'}
        data = {'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'cameraID': '5ae0ecbd336359291be74c12', 'type': 'ip',
                'retrieval': '{"ip": null, "port": "8080", "brand": "test_brand", "model": "test_model", '
                             '"image_path": "test_image_path", "video_path": "test_vid_path"}'}
        with self.assertRaises(ResourceNotFoundError):
            client.update_camera(cameraID='5ae0ecbd336359291be74c12', camera_type='ip',
                                 is_active_image=False, is_active_video=True, legacy_cameraID=000000000,
                                 source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                 state='Indiana', city='West Lafayette', resolution_width=720,
                                 resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                 timezone_name='test_t_name', reference_logo='test_ref_logo',
                                 reference_url='test_ref_url', port='8080', brand='test_brand',
                                 model='test_model', image_path='test_image_path', video_path='test_vid_path')
        mock_put.assert_called_once_with(url, headers=headers, data=data)
        self.assertEqual(1, mock_response.json.call_count)

if __name__ == '__main__':
    unittest.main()
