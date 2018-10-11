"""
This module contains test cases for client class methods
"""
import unittest
import sys
from os import path
import mock
import CAM2CameraDatabaseAPIClient as cam2
from CAM2CameraDatabaseAPIClient.camera import NonIPCamera
from CAM2CameraDatabaseAPIClient.config import SECRET_LENGTH, CLIENTID_LENGTH
from CAM2CameraDatabaseAPIClient.error import AuthenticationError, InternalError,\
     InvalidClientIdError, InvalidClientSecretError, ResourceNotFoundError,\
     FormatError, AuthorizationError
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class BaseClientTest(unittest.TestCase):
    """
    Test all requests from
    with different scenarios
    https://purduecam2project.github.io/CameraDatabaseAPI/
    """
    def setUp(self):
        self.base_URL = 'https://cam2-api.herokuapp.com/'
        self.token_url = self.base_URL + 'auth'
        self.token_params = {'clientID': '0' * CLIENTID_LENGTH,
                             'clientSecret': '0' * SECRET_LENGTH}

class InitClientTest(BaseClientTest):

    def test_client_init_wrong_CLIENTID_LENGTH(self):
        with self.assertRaises(InvalidClientIdError):
            client = cam2.Client('dummyID', '0' * SECRET_LENGTH)
            return client

    def test_client_init_wrong_Client_SECRET_LENGTH(self):
        # client secret shorter than SECRET_LENGTH
        with self.assertRaises(InvalidClientSecretError):
            client = cam2.Client('0' * CLIENTID_LENGTH, 'dummySecret')
            return client

    def test_client_init(self):
        clientID = '0' * CLIENTID_LENGTH
        clientSecret = '0' * SECRET_LENGTH
        client = cam2.Client(clientID, clientSecret)
        self.assertTrue(isinstance(client, cam2.Client))
        self.assertEqual(client.clientID, clientID, 'ID not stored in the client object.')
        self.assertEqual(client.clientSecret, clientSecret,
                         'Secret not stored in the client object.')
        self.assertIs(client.token, None, 'Token not set to default')

        # client secret longer than SECRET_LENGTH
        clientSecret2 = '0' * 80
        client2 = cam2.Client(clientID, clientSecret2)
        self.assertTrue(isinstance(client2, cam2.Client))
        self.assertEqual(client2.clientID, clientID, 'ID not stored in the client object.')
        self.assertEqual(client2.clientSecret, clientSecret2,
                         'Secret not stored in the client object.')
        self.assertIs(client2.token, None, 'Token not set to default')

    def test_build_header(self):
        clientID = '0' * CLIENTID_LENGTH
        clientSecret = '0' * SECRET_LENGTH
        client = cam2.Client(clientID, clientSecret)
        client.token = 'dummy'
        head_example = {'Authorization': 'Bearer ' + 'dummy'}
        self.assertEqual(client.header_builder(), head_example)

class RequestTokenTest(BaseClientTest):

    def setUp(self):
        super(RequestTokenTest, self).setUp()
        self.params = {'clientID': '0' * CLIENTID_LENGTH, 'clientSecret': '0' * SECRET_LENGTH}
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)

    @mock.patch('CAM2CameraDatabaseAPIClient.error.AuthenticationError')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_token_incorrect_ID_Secret(self, mock_get, mock_http_error_handler):
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Cannot find client with that ClientID"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(ResourceNotFoundError):
            self.client._request_token()
        mock_get.assert_called_once_with(self.token_url, params=self.params)
        self.assertEqual(1, mock_response.json.call_count)
        return mock_http_error_handler

    @mock.patch('CAM2CameraDatabaseAPIClient.error.AuthenticationError')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_token_incorrect_Secret(self, mock_get, mock_http_error_handler):
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Bad client secret"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(AuthenticationError):
            self.client._request_token()
        mock_get.assert_called_once_with(self.token_url, params=self.params)
        self.assertEqual(1, mock_response.json.call_count)
        return mock_http_error_handler

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_token_all_correct(self, mock_get):
        mock_response = mock.Mock()
        expected_dict = {
            "token": "correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_dict = self.client._request_token()

        mock_get.assert_called_once_with(self.token_url, params=self.params)
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(self.client.token, 'correctToken',
                         'token not stored in the client object.')
        return response_dict

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_token_all_correct_Internal_error(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(InternalError):
            self.client._request_token()
        mock_get.assert_called_once_with(self.token_url, params=self.params)
        self.assertEqual(0, mock_response.json.call_count)

class RegisterTest(BaseClientTest):

    def setUp(self):
        super(RegisterTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.data = {'owner': 'testowner', 'permissionLevel': 'user'}
        self.url = self.base_URL + 'apps/register'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_register(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
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

        resultID, resultSecret = self.client.register('testowner')
        mock_post.assert_called_once_with(self.url, headers=self.header, data=self.data)
        self.assertEqual(resultID, expected_clientID)
        self.assertEqual(resultSecret, expected_clientSecret)
        self.assertEqual(2, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_register_expired_token_success(self, mock_get, mock_post):
        self.client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.',
        }
        # set second request.post's result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'clientID': 'test_clientID',
            'clientSecret': 'test_clientSecret'
        }
        mock_post.side_effect = [mock_response, mock_response2]
        # set _request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.return_value = mock_get_response
        # run the test
        resultID, resultSecret = self.client.register('testowner')
        self.assertEqual(resultID, 'test_clientID')
        self.assertEqual(resultSecret, 'test_clientSecret')
        mock_get.assert_called_with(self.token_url, params=self.token_params)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_register_expired_token_failure(self, mock_get, mock_post):
        self.client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.',
        }
        mock_post.return_value = mock_response
        # set _request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.return_value = mock_get_response
        # run the test
        with self.assertRaises(AuthenticationError):
            self.client.register('testowner')

        mock_get.assert_called_with(self.token_url, params=self.token_params)
        self.assertEqual(3, mock_post.call_count)
        self.assertEqual(2, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_register_no_owner(self, mock_post):
        self.client.token = "correctToken"
        # set request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Must include the owner's username"
        }
        mock_post.return_value = mock_response
        # validate result

        with self.assertRaises(FormatError):
            self.client.register('testowner')
        mock_post.assert_called_once_with(self.url, headers=self.header, data=self.data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_register_incorrect_clientID(self, mock_get):

        # incorrect clientID in this case can only cause 404 error
        # in request token function.
        # which will only be called:
        # 1: when no token exists for the client object
        # 2: when previous token expires

        # this testcase test for the first scenario.
        # the function exits before makeing the register api call.

        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "No app exists with given clientID"
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ResourceNotFoundError):
            self.client.register('testowner')

        mock_get.assert_called_once_with(self.token_url, params=self.token_params)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_register_internal_error(self, mock_post):

        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        # validate result

        with self.assertRaises(InternalError):
            self.client.register('testowner')
        mock_post.assert_called_once_with(self.url, headers=self.header, data=self.data)
        self.assertEqual(0, mock_response.json.call_count)

class GetClientIDTest(BaseClientTest):

    def setUp(self):
        super(GetClientIDTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.param = {'owner': 'testowner'}
        self.url = self.base_URL + 'apps/by-owner'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_clientID_by_owner_all_correct(self, mock_get):

        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        clientObject = [
            {'clientID': 'test_clientID1'},
            {'clientID': 'test_clientID2'}]
        mock_response.json.return_value = clientObject

        mock_get.return_value = mock_response
        expected_clientID_array = ['test_clientID1', 'test_clientID2']
        self.assertEqual(self.client.client_ids_by_owner("testowner"), expected_clientID_array)
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_clientID_by_owner_expired_token_success(self, mock_get):
        self.client.token = "ExpiredToken"
        # set first requests.get's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.',
        }
        # set _request_token()'s result
        mock_response1 = mock.Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'token': 'correctToken'
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
        self.client.client_ids_by_owner('testowner')
        self.assertEqual(3, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_clientID_by_owner_expired_token_failure(self, mock_get):
        self.client.token = "ExpiredToken"
        # set first requests.get's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.',
        }
        # set _request_token()'s result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        # run the test
        with self.assertRaises(AuthenticationError):
            self.client.client_ids_by_owner('testowner')
        self.assertEqual(5, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_clientID_by_owner_incorrect_clientID(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given clientID'
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ResourceNotFoundError):
            self.client._request_token()
        mock_get.assert_called_once_with(self.token_url, params=self.token_params)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_clientID_by_owner_internal_error(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(InternalError):
            self.client.client_ids_by_owner('testowner')
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)
        self.assertEqual(0, mock_response.json.call_count)

class GetUsageTest(BaseClientTest):

    def setUp(self):
        super(GetUsageTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.param = {'owner': 'testowner'}
        self.url = self.base_URL + 'apps/1/usage'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_clientID_all_correct(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'api_usage': 7
        }
        mock_get.return_value = mock_response

        self.assertEqual(self.client.usage_by_client('1', 'testowner'), 7)
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_client_expired_token_success(self, mock_get):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_response1 = mock.Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'token': 'correctToken'
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'api_usage': 1
        }
        mock_get.side_effect = [mock_response, mock_response1, mock_response2]
        self.assertEqual(1, self.client.usage_by_client('1', 'testowner'))
        self.assertEqual(3, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_client_expired_token_failure(self, mock_get):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.usage_by_client('1', 'testowner')
        self.assertEqual(5, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=self.param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_client_authorization_error(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'message': 'Forbidden to view API usage of this client'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(AuthorizationError):
            self.client.usage_by_client('1', 'testowner')
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_client_id_not_found(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given clientID'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(ResourceNotFoundError):
            self.client.usage_by_client('1', 'testowner')
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_usage_by_client_internal_error(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(InternalError):
            self.client.usage_by_client('1', 'testowner')
        mock_get.assert_called_once_with(self.url, headers=self.header, params=self.param)
        self.assertEqual(0, mock_response.json.call_count)

class UpdateOwnerTest(BaseClientTest):

    def setUp(self):
        super(UpdateOwnerTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.data = {'owner': 'testowner'}
        self.url = self.base_URL + 'apps/1'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_owner(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'OK'
        }
        mock_put.return_value = mock_response
        self.assertEqual(self.client.update_owner('1', 'testowner'), 'OK')
        mock_put.assert_called_once_with(self.url, headers=self.header, data=self.data)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_update_owner_expired_token_success(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
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
            'token': 'correctToken'
        }
        mock_get.return_value = mock_response2
        self.assertEqual('OK', self.client.update_owner('1', 'testowner'))
        headers = {'Authorization': 'Bearer ExpiredToken'}

        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_update_owner_expired_token_failure(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_put.return_value = mock_response

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken',
        }
        mock_get.return_value = mock_response2
        with self.assertRaises(AuthenticationError):
            self.client.update_owner('1', 'testowner')
        self.assertEqual(3, mock_put.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}

        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_owner_invalid_clientid(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given client id.'
        }
        mock_put.return_value = mock_response
        with self.assertRaises(ResourceNotFoundError):
            self.client.update_owner('1', 'testowner')
        mock_put.assert_called_once_with(self.url, headers=self.header, data=self.data)
        self.assertEqual(1, mock_response.json.call_count)

class UpdatePermissionTest(BaseClientTest):

    def setUp(self):
        super(UpdatePermissionTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.data = {'permissionLevel': 'user'}
        self.url = self.base_URL + 'apps/1'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_permissionLevel(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'OK'
        }
        mock_put.return_value = mock_response
        self.assertEqual(self.client.update_permission('1', 'user'), 'OK')
        mock_put.assert_called_once_with(self.url, headers=self.header, data=self.data)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_update_permissionLevel_expired_token_success(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
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
            'token': 'correctToken',
        }
        mock_get.return_value = mock_response2
        self.assertEqual(self.client.update_permission('1', 'user'), 'OK')
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_update_permissionLevel_expired_token_failure(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_put.return_value = mock_response

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken',
        }
        mock_get.return_value = mock_response2
        with self.assertRaises(AuthenticationError):
            self.client.update_permission('1', 'user')
        self.assertEqual(3, mock_put.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}

        call_list = [mock.call(self.url, headers=headers, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data),
                     mock.call(self.url, headers=self.header, data=self.data)]
        self.assertEqual(mock_put.call_args_list, call_list)

class ResetSecretTest(BaseClientTest):

    def setUp(self):
        super(ResetSecretTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'apps/1/secret'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_reset_secret(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'clientSecret': 'test_clientSecret'
        }
        mock_put.return_value = mock_response
        self.assertEqual(self.client.reset_secret('1'), 'test_clientSecret')
        mock_put.assert_called_once_with(self.url, headers=self.header, data=None)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_reset_secret_invalid_clientid(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given client id.'
        }
        mock_put.return_value = mock_response
        with self.assertRaises(ResourceNotFoundError):
            self.client.reset_secret('1')
        mock_put.assert_called_once_with(self.url, headers=self.header, data=None)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_reset_secret_expired_token_success(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = {
            'clientSecret': 'test_clientSecret'
        }
        mock_put.side_effect = [mock_response, mock_response3]

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.return_value = mock_response2
        self.assertEqual('test_clientSecret', self.client.reset_secret('1'))
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, data=None),
                     mock.call(self.url, headers=self.header, data=None)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_reset_secret_expired_token_failure(self, mock_get, mock_put):
        self.client.token = "ExpiredToken"
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        mock_put.return_value = mock_response

        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken',
        }
        mock_get.return_value = mock_response2
        with self.assertRaises(AuthenticationError):
            self.client.reset_secret('1')
        self.assertEqual(3, mock_put.call_count)
        self.assertEqual(2, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, data=None),
                     mock.call(self.url, headers=self.header, data=None),
                     mock.call(self.url, headers=self.header, data=None)]
        self.assertEqual(mock_put.call_args_list, call_list)

class GetCamIDTest(BaseClientTest):

    def setUp(self):
        super(GetCamIDTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'cameras/12345'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_id_all_correct(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = {
            'camera_type': 'ip',
            'ip': '210.1.1.2',
            'latitude': '44.9087',
            'longitude': '-129.09',
            'port': '80'
        }
        mock_dict = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.2',
                'port': '80'
            }
        }
        mock_response.json.return_value = mock_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertEqual(self.client.camera_by_id('12345'), expected_dict)
        mock_get.assert_called_once_with(self.url, headers=self.header)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_id_expired_token_success(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        expected_dict = {
            'camera_type': 'ip',
            'ip': '210.1.1.2',
            'latitude': '44.9087',
            'longitude': '-129.09',
            'port': '80'
        }
        mock_dict = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.2',
                'port': '80'
            }
        }
        mock_response3.json.return_value = mock_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        self.assertEqual(self.client.camera_by_id('12345'), expected_dict)
        self.assertEqual(3, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_id_expired_token_failure(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.camera_by_id('12345')
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_id_format_error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'message': 'Format Error'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(FormatError):
            self.client.camera_by_id('12345')
        mock_get.assert_called_once_with(self.url, headers=self.header)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_id_internal_error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(InternalError):
            self.client.camera_by_id('12345')
        mock_get.assert_called_once_with(self.url, headers=self.header)

class GetLegacyCamIDTest(BaseClientTest):

    def setUp(self):
        super(GetLegacyCamIDTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'cameras/legacy/12345'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_legacy_id_all_correct(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = {
            'camera_type': 'ip',
            'ip': '210.1.1.2',
            'latitude': '44.9087',
            'longitude': '-129.09',
            'port': '80'
        }
        mock_dict = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.2',
                'port': '80'
            }
        }
        mock_response.json.return_value = mock_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertEqual(self.client.camera_by_legacy_id('12345'), expected_dict)
        mock_get.assert_called_once_with(self.url, headers=self.header)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_legacy_id_expired_token_success(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        expected_dict = {
            'camera_type': 'ip',
            'ip': '210.1.1.2',
            'latitude': '44.9087',
            'longitude': '-129.09',
            'port': '80'
        }
        mock_dict = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.2',
                'port': '80'
            }
        }
        mock_response3.json.return_value = mock_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        self.assertEqual(self.client.camera_by_legacy_id('12345'), expected_dict)
        self.assertEqual(3, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_legacy_id_expired_token_failure(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.camera_by_legacy_id('12345')
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=None)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_legacy_id_format_error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'message': 'Format Error'
        }
        mock_get.return_value = mock_response
        with self.assertRaises(FormatError):
            self.client.camera_by_legacy_id('12345')
        mock_get.assert_called_once_with(self.url, headers=self.header)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_legacy_id_internal_error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(InternalError):
            self.client.camera_by_legacy_id('12345')
        mock_get.assert_called_once_with(self.url, headers=self.header)

class GetCameraByListIDTest(BaseClientTest):

    def setUp(self):
        super(GetCameraByListIDTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.legacy_url = self.base_URL + 'cameras/legacy/12345'
        self.url = self.base_URL + 'cameras/12345'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_by_list_id_all_correct(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = [{'camera_type': 'ip',
                          'ip': '210.1.1.2',
                          'latitude': '44.9087',
                          'longitude': '-129.09',
                          'port': '80'},
                         {'camera_type': 'ip',
                          'ip': '210.1.1.3',
                          'latitude': '44.9087',
                          'longitude': '-129.09',
                          'port': '80'}]
        mock_dict = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.2',
                'port': '80'
            }
        }
        mock_response.json.return_value = mock_dict
        mock_response.status_code = 200

        mock_response1 = mock.Mock()
        mock_dict1 = {
            "longitude": "-129.09",
            "latitude": "44.9087",
            'type': 'ip',
            'retrieval': {
                'ip': '210.1.1.3',
                'port': '80'
            }
        }
        mock_response1.json.return_value = mock_dict1
        mock_response1.status_code = 200
        mock_get.side_effect = [mock_response, mock_response1]
        self.assertEqual(self.client.camera_by_list_id(["12345"], ["12345"]), expected_dict)
        self.assertEqual(2, mock_get.call_count)
        call_list = [mock.call(self.url, headers=self.header),
                     mock.call(self.legacy_url, headers=self.header)]
        self.assertEqual(mock_get.call_args_list, call_list)

class SearchCamTest(BaseClientTest):

    def setUp(self):
        super(SearchCamTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'cameras/search'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_empty(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = []
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_list = self.client.search_camera(offset=10000)
        mock_get.assert_called_once_with(self.url, headers=self.header, params={'offset': 10000})
        self.assertEqual(1, mock_get.call_count)
        actual_list = []
        self.assertEqual(response_list, actual_list,
                         'Returned json is not tranlated correctly')
        return response_list

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_no_param(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()

        # without params user should get 1st 100 cameras
        expected_dict = [{"legacy_cameraID": 31280, "type": "non_ip", "source": "webcam_jp",
                          "country": "JP", "state": None, "city": None, "resolution_width": 1,
                          "resolution_height": 1, "is_active_image": True,
                          "is_active_video": False, "utc_offset": 32400, "timezone_id": None,
                          "timezone_name": None, "reference_logo": "webtral.jpg",
                          "reference_url": "http://some_url",
                          "cameraID": "5b0e74213651360004edb426",
                          "retrieval": {"snapshot_url": "http://images./preview/adf.jpg"},
                          "latitude": 35.8876, "longitude": 136.098}] * 100
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_list = self.client.search_camera()
        mock_get.assert_called_once_with(self.url, headers=self.header, params={})
        self.assertEqual(1, mock_get.call_count)

        cam_entries = {"legacy_cameraID": 31280, "camera_type": "non_ip", "source": "webcam_jp",
                       "country": "JP", "state": None, "city": None, "resolution_width": 1,
                       "resolution_height": 1, "is_active_image": True,
                       "is_active_video": False, "utc_offset": 32400, "timezone_id": None,
                       "timezone_name": None, "reference_logo": "webtral.jpg",
                       "reference_url": "http://some_url", "cameraID": "5b0e74213651360004edb426",
                       "snapshot_url": "http://images./preview/adf.jpg",
                       "latitude": 35.8876, "longitude": 136.098}
        cam = NonIPCamera(**cam_entries)
        actual_list = [cam] * 100
        for i in range(100):
            self.assertEqual(response_list[i], actual_list[i])
        return response_list

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_no_token(self, mock_get):
        mock_response = mock.Mock()
        expected_dict = {
            "token": "correctToken"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        with self.assertRaises(TypeError):
            self.client.search_camera(country='USA')
        mock_get.assert_called_with(self.url, headers=self.header, params={'country': 'USA'})
        self.assertEqual(2, mock_get.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_Expired_Token_failure(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.search_camera(country='USA')

        headers = {'Authorization': 'Bearer ExpiredToken'}
        search_params = {'country': 'USA'}
        call_list = [mock.call(self.url, headers=headers, params=search_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=search_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=search_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_Expired_Token_success(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200

        expected_dict = []
        mock_response3.json.return_value = expected_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        self.assertEqual(self.client.search_camera(country='JP'), expected_dict,
                         'Empty camera list is not correctly parsed.')
        self.assertEqual(3, mock_get.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        search_params = {'country': 'JP'}
        call_list = [mock.call(self.url, headers=headers, params=search_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=search_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_Expired_Token_format_error(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.status_code = 422
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response3.json.return_value = expected_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        with self.assertRaises(FormatError):
            self.client.search_camera(offset='JP')
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual(1, mock_response3.json.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        search_params = {'offset': 'JP'}
        call_list = [mock.call(self.url, headers=headers, params=search_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=search_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_Expired_Token_internal_error(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.status_code = 500
        expected_dict = {
            "message": "Internal error"
        }
        mock_response3.json.return_value = expected_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        with self.assertRaises(InternalError):
            self.client.search_camera(country='JP')
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual(0, mock_response3.json.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        search_params = {'country': 'JP'}
        call_list = [mock.call(self.url, headers=headers, params=search_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=search_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_all_correct_Internal_Error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(InternalError):
            self.client.search_camera(country='USA')
        mock_get.assert_called_once_with(self.url, headers=self.header, params={'country': 'USA'})
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_Format_Error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 422
        mock_get.return_value = mock_response

        with self.assertRaises(FormatError):
            self.client.search_camera(resolution_width='USA')
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={'resolution_width': 'USA'})
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_search_camera_all_correct(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = [{"legacy_cameraID":31280, "type":"non_ip", "source":"webcam_jp",
                          "country":"JP", "state":None, "city":None, "resolution_width":1,
                          "resolution_height":1, "is_active_image":True,
                          "is_active_video":False, "utc_offset":32400, "timezone_id":None,
                          "timezone_name":None, "reference_logo":"webtral.jpg",
                          "reference_url":"http://some_url", "cameraID":"5b0e74213651360004edb426",
                          "retrieval":{"snapshot_url":"http://images./preview/adf.jpg"},
                          "latitude":35.8876, "longitude":136.098}]
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_list = self.client.search_camera(
            country='JP', camera_type='non_ip', is_active_image=True, offset=100)
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={
                                             'country': 'JP',
                                             'type': 'non_ip',
                                             'is_active_image': True,
                                             'offset': 100})
        self.assertEqual(1, mock_get.call_count)
        actual_dict = {"legacy_cameraID":31280, "camera_type":"non_ip", "source":"webcam_jp",
                       "country":"JP", "state":None, "city":None, "resolution_width":1,
                       "resolution_height":1, "is_active_image":True,
                       "is_active_video":False, "utc_offset":32400, "timezone_id":None,
                       "timezone_name":None, "reference_logo":"webtral.jpg",
                       "reference_url":"http://some_url", "cameraID":"5b0e74213651360004edb426",
                       "snapshot_url":"http://images./preview/adf.jpg",
                       "latitude":35.8876, "longitude":136.098}
        self.assertEqual(response_list[0], actual_dict,
                         'Returned json is not tranlated correctly')

    def test_search_camera_only_illegal_args(self):
        self.client.token = 'correctToken'
        kwargs = {'illegal': 'test_lad'}
        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)

    def test_search_camera_illegal_args(self):
        self.client.token = 'correctToken'
        kwargs = {'illegal': 'test_lad', 'image_path': 'test', 'video_path': 'test'}
        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)

class CamExistTest(BaseClientTest):

    def setUp(self):
        super(CamExistTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'cameras/exist'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_cam_exist_all_correct_cam_list(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()

        expected_dict = [{"legacy_cameraID":31280, "type":"non_ip", "source":"webcam_jp",
                          "country":"JP", "state":None, "city":None, "resolution_width":1,
                          "resolution_height":1, "is_active_image":True,
                          "is_active_video":False, "utc_offset":32400, "timezone_id":None,
                          "timezone_name":None, "reference_logo":"webtral.jpg",
                          "reference_url":"http://some_url", "cameraID":"5b0e74213651360004edb426",
                          "retrieval":{"snapshot_url":"/preview/adf.jpg"},
                          "latitude":35.8876, "longitude":136.098}] * 2
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_list = self.client.check_cam_exist(
            camera_type='non_ip',
            snapshot_url='/preview/adf.jpg')
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={
                                             'type': 'non_ip',
                                             'snapshot_url': '/preview/adf.jpg'
                                             })
        self.assertEqual(1, mock_get.call_count)

        cam_entries = {"legacy_cameraID":31280, "camera_type":"non_ip", "source":"webcam_jp",
                       "country":"JP", "state":None, "city":None, "resolution_width":1,
                       "resolution_height":1, "is_active_image":True,
                       "is_active_video":False, "utc_offset":32400, "timezone_id":None,
                       "timezone_name":None, "reference_logo":"webtral.jpg",
                       "reference_url":"http://some_url", "cameraID":"5b0e74213651360004edb426",
                       "snapshot_url":"/preview/adf.jpg",
                       "latitude":35.8876, "longitude":136.098}
        cam = NonIPCamera(**cam_entries)
        actual_list = [cam] * 2
        for i in range(2):
            self.assertEqual(response_list[i], actual_list[i])

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_all_correct_empty(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_dict = []
        mock_response.json.return_value = mock_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response_list = self.client.check_cam_exist(camera_type='stream', m3u8_url='test_url')
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={'type': 'stream', 'm3u8_url': 'test_url'})
        actual_dict = []
        self.assertEqual(response_list, actual_dict, 'Returned json is not tranlated correctly')

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_eixst_expired_token_success(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        expected_dict = []
        mock_dict = []
        mock_response3.json.return_value = mock_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        self.assertEqual(
            self.client.check_cam_exist(camera_type='stream', m3u8_url='test_url'),
            expected_dict
        )
        self.assertEqual(3, mock_get.call_count)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        match_params = {'type': 'stream', 'm3u8_url': 'test_url'}
        call_list = [mock.call(self.url, headers=headers, params=match_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=match_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_Expired_Token_failure(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.check_cam_exist(camera_type='stream', m3u8_url='test_url')

        headers = {'Authorization': 'Bearer ExpiredToken'}
        match_params = {'type': 'stream', 'm3u8_url': 'test_url'}
        call_list = [mock.call(self.url, headers=headers, params=match_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=match_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=match_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_Expired_Token_format_error(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.status_code = 422
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response3.json.return_value = expected_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        with self.assertRaises(FormatError):
            self.client.check_cam_exist(camera_type='ip')
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual(1, mock_response3.json.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        match_params = {'type': 'ip'}
        call_list = [mock.call(self.url, headers=headers, params=match_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=match_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_Expired_Token_internal_error(self, mock_get):
        self.client.token = 'ExpiredToken'
        # set result for first search camera
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        # set result for _request_token()
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'token': 'correctToken'
        }
        # set result for second search camera
        mock_response3 = mock.Mock()
        mock_response3.status_code = 500
        expected_dict = {
            "message": "Internal error"
        }
        mock_response3.json.return_value = expected_dict
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]
        with self.assertRaises(InternalError):
            self.client.check_cam_exist(camera_type='ip', image_path='test_url')
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual(0, mock_response3.json.call_count)

        headers = {'Authorization': 'Bearer ExpiredToken'}
        match_params = {'type': 'ip', 'image_path': 'test_url'}
        call_list = [mock.call(self.url, headers=headers, params=match_params),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=match_params)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_all_correct_Internal_Error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(InternalError):
            self.client.check_cam_exist(camera_type='ip', image_path='test_url',
                                        video_path='test_url')
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={
                                             'type': 'ip',
                                             'image_path': 'test_url',
                                             'video_path': 'test_url'
                                             })
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_camera_exist_Format_Error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 422
        mock_get.return_value = mock_response
        with self.assertRaises(FormatError):
            self.client.check_cam_exist(camera_type='iip', image_path='test_url',
                                        video_path='test_url')
        mock_get.assert_called_once_with(self.url, headers=self.header,
                                         params={
                                             'type': 'iip',
                                             'image_path': 'test_url',
                                             'video_path': 'test_url'
                                             })
        self.assertEqual(1, mock_response.json.call_count)

    def test_camera_exist_illegal_args(self):
        self.client.token = 'correctToken'
        kwargs = {'illegal': 'test_lad', 'camera_type': 'ip', 'image_path': 'test_url',
                  'ip': 'test_ip', 'video_path': 'test_vid_path'}

        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)

class ChangeLogTest(BaseClientTest):

    def setUp(self):
        super(ChangeLogTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.url = self.base_URL + 'apps/db-change'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_all_correct(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 200
        clientObject = [
            {
                'cameraID': '5ae0ecbd336359291be74c12',
                'timestamp': '2018-07-04T19:52:52.337Z',
            },
            {
                'cameraID': '5ae0ecbd336312391be74c12',
                'timestamp': '2018-07-04T20:52:52.337Z',
            },
            {
                'cameraID': '5ae0ecbd336354291be74c12',
                'timestamp': '2018-07-04T21:52:52.337Z',
            },
        ]
        mock_response.json.return_value = clientObject
        mock_get.return_value = mock_response
        param = {'start': None,
                 'end': None,
                 'offset': None}
        self.assertEqual(self.client.get_change_log(), clientObject)
        mock_get.assert_called_once_with(self.url, headers=self.header, params=param)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_expired_token_success(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_response3 = mock.Mock()
        mock_response3.status_code = 200
        clientObject = [
            {
                'cameraID': '5ae0ecbd336359291be74c12',
                'timestamp': '2018-07-04T19:52:52.337Z',
            },
            {
                'cameraID': '5ae0ecbd336312391be74c12',
                'timestamp': '2018-07-04T20:52:52.337Z',
            },
            {
                'cameraID': '5ae0ecbd336354291be74c12',
                'timestamp': '2018-07-04T21:52:52.337Z',
            },
        ]
        mock_response3.json.return_value = clientObject
        mock_get.side_effect = [mock_response, mock_response2, mock_response3]

        self.assertEqual(self.client.get_change_log(start='2018-07-04T19:52:52.337Z',
                                                    end='2018-07-05T19:52:52.337Z',
                                                    offset=1000), clientObject)
        self.assertEqual(3, mock_get.call_count)
        param = {'start': '2018-07-04T19:52:52.337Z',
                 'end': '2018-07-05T19:52:52.337Z',
                 'offset': 1000}
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [mock.call(self.url, headers=headers, params=param),
                     mock.call(self.token_url, params=self.token_params),
                     mock.call(self.url, headers=self.header, params=param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_expired_token_failure(self, mock_get):
        self.client.token = 'ExpiredToken'
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Token expired."
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "token": "correctToken"
        }
        mock_get.side_effect = [mock_response, mock_response2, mock_response,
                                mock_response2, mock_response]
        with self.assertRaises(AuthenticationError):
            self.client.get_change_log()
        param = {'start': None,
                 'end': None,
                 'offset': None}
        headers = {'Authorization': 'Bearer ExpiredToken'}
        call_list = [
            mock.call(self.url, headers=headers, params=param),
            mock.call(self.token_url, params=self.token_params),
            mock.call(self.url, headers=self.header, params=param),
            mock.call(self.token_url, params=self.token_params),
            mock.call(self.url, headers=self.header, params=param)]
        self.assertEqual(mock_get.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_format_error(self, mock_get):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Format Error"
        }
        mock_get.return_value = mock_response
        with self.assertRaises(FormatError):
            self.client.get_change_log()
        param = {'start': None,
                 'end': None,
                 'offset': None}
        mock_get.assert_called_once_with(self.url, headers=self.header, params=param)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_resource_not_found_error(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "Resource Not Found Error"
        }
        mock_get.return_value = mock_response
        with self.assertRaises(ResourceNotFoundError):
            self.client.get_change_log()
        mock_get.assert_called_once_with(self.token_url, params=self.token_params)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_get_change_log_with_internal_error(self, mock_get):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(InternalError):
            self.client.get_change_log()

        param = {'start': None,
                 'end': None,
                 'offset': None}
        mock_get.assert_called_once_with(self.url, headers=self.header, params=param)

class WriteCamTest(BaseClientTest):

    def setUp(self):
        super(WriteCamTest, self).setUp()
        self.client = cam2.Client('0' * CLIENTID_LENGTH, '0' * SECRET_LENGTH)
        self.header = {'Authorization': 'Bearer correctToken'}
        self.expected_cameraID = '5ae0ecbd336359291be74c12'
        self.update_url = self.base_URL + 'cameras/' + self.expected_cameraID
        self.create_url = self.base_URL + 'cameras/create'

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_ip(self, mock_put):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID
        }

        mock_put.return_value = mock_response
        # validate result
        data = {'type': 'ip', 'frame_rate': 10,
                'retrieval': '{"brand": null, "image_path": null,'
                             ' "ip": null, "model": null, "port": null,'
                             ' "video_path": "path/video"}'}
        kwargs = {'cameraID': self.expected_cameraID, 'camera_type': 'ip', 'frame_rate': 10,
                  'video_path': 'path/video'}

        resultID = self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_non_ip(self, mock_put):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID
        }
        mock_put.return_value = mock_response
        # validate result
        data = {'is_active_image': False, 'type': 'non_ip',
                'retrieval': '{"snapshot_url": "test_snapshot"}'}
        kwargs = {'is_active_image': False, 'camera_type': 'non_ip',
                  'snapshot_url': 'test_snapshot', 'cameraID': self.expected_cameraID}
        resultID = self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_stream_no_type(self, mock_put):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID
        }
        mock_put.return_value = mock_response
        # validate result
        data = {'m3u8_url': 'test_m3u8', 'type': None}
        kwargs = {'m3u8_url': 'test_m3u8', 'cameraID': self.expected_cameraID}

        resultID = self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_update_camera_expired_token_success(self, mock_get, mock_put):
        self.client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.'
        }
        # set second request.post's result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'cameraID': self.expected_cameraID
        }
        mock_put.side_effect = [mock_response, mock_response2]
        # set _request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.return_value = mock_get_response

        kwargs = {'reference_url': 'url.com/ref', 'reference_logo': 'Logo',
                  'timezone_name': 'Test', 'cameraID': self.expected_cameraID}

        resultID = self.client.write_camera(**kwargs)
        self.assertEqual(resultID, self.expected_cameraID)

        mock_get.assert_called_with(self.token_url, params=self.token_params)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        data = {'reference_url': 'url.com/ref', 'reference_logo': 'Logo',
                'timezone_name': 'Test', 'type': None}

        call_list = [mock.call(self.update_url, headers=headers, data=data),
                     mock.call(self.update_url, headers=self.header, data=data)]
        self.assertEqual(mock_put.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_internal_error(self, mock_put):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_put.return_value = mock_response
        # validate result
        data = {'is_active_image': True, 'type': 'ip',
                'retrieval': '{"brand": "Some Brand", "image_path": "path/image",'
                             ' "ip": "127.0.0.2", "model": "Some model", "port": "8080",'
                             ' "video_path": "path/video"}'}
        kwargs = {'cameraID': self.expected_cameraID, 'is_active_image': True,
                  'camera_type': 'ip', 'ip': '127.0.0.2', 'port': '8080', 'brand': 'Some Brand',
                  'model': 'Some model', 'image_path': 'path/image', 'video_path': 'path/video'}

        with self.assertRaises(InternalError):
            self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_all_correct_Format_Error(self, mock_put):
        self.client.token = 'correctToken'
        mock_response = mock.Mock()
        expected_dict = {
            "message": "Format Error Messages"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 422
        mock_put.return_value = mock_response
        data = {'is_active_image': 'not false', 'type': 'undefined'}
        kwargs = {'cameraID': self.expected_cameraID, 'is_active_image': 'not false',
                  'camera_type': 'undefined'}

        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.put')
    def test_update_camera_invalid_clientID(self, mock_put):
        self.client.token = "correctToken"
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'message': 'No app exists with given client id.'
        }
        mock_put.return_value = mock_response
        data = {'reference_url': 'url.com/ref', 'type': None}
        kwargs = {'cameraID': self.expected_cameraID, 'reference_url': 'url.com/ref'}
        with self.assertRaises(ResourceNotFoundError):
            self.client.write_camera(**kwargs)
        mock_put.assert_called_once_with(self.update_url, headers=self.header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_ip(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID,
        }
        mock_post.return_value = mock_response

        data = {'resolution_height': 312, 'resolution_width': 123,
                'longitude': '100.21323', 'latitude': '-44.9281',
                'legacy_cameraID': None, 'm3u8_url': 'sample.com/m3u8_url',
                'snapshot_url': 'sample.com/snapshot_url', 'is_active_video': False,
                'is_active_image': True, 'type': 'ip', 'frame_rate': 10,
                'retrieval': '{"brand": "Some Brand", "image_path": "path/image",'
                             ' "ip": "127.0.0.2", "model": "Some model", "port": "8080",'
                             ' "video_path": "path/video"}'}
        kwargs = {'resolution_height': 312, 'resolution_width': 123, 'longitude': '100.21323',
                  'latitude': '-44.9281', 'legacy_cameraID': None, 'frame_rate': 10,
                  'm3u8_url': 'sample.com/m3u8_url', 'snapshot_url': 'sample.com/snapshot_url',
                  'is_active_video': False, 'is_active_image': True, 'camera_type': 'ip',
                  'ip': '127.0.0.2', 'port': '8080', 'brand': 'Some Brand',
                  'model': 'Some model', 'image_path': 'path/image', 'video_path': 'path/video'}
        resultID = self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_only_ip(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID,
        }
        mock_post.return_value = mock_response
        # validate result

        data = {'is_active_video': False, 'is_active_image': True, 'type': 'ip',
                'retrieval': '{"brand": null, "image_path": null,'
                             ' "ip": "test_ip", "model": null, "port": null,'
                             ' "video_path": null}'}
        kwargs = {'is_active_video': False, 'is_active_image': True,
                  'camera_type': 'ip', 'ip': 'test_ip'}
        resultID = self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_non_ip(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID,
        }
        mock_post.return_value = mock_response
        # validate result
        data = {'resolution_height': 480, 'resolution_width': 720, 'city': 'West Lafayette',
                'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                'is_active_video': True, 'is_active_image': False,
                'type': 'non_ip', 'retrieval': '{"snapshot_url": "test_snapshot"}'}

        kwargs = {'resolution_height': 480, 'resolution_width': 720, 'city': 'West Lafayette',
                  'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                  'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                  'is_active_video': True, 'is_active_image': False, 'camera_type': 'non_ip',
                  'snapshot_url': 'test_snapshot'}
        resultID = self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_no_snapshot_url(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Format Error Messages",
        }
        mock_post.return_value = mock_response
        # validate result
        data = {'is_active_video': True, 'is_active_image': False, 'type': 'non_ip',
                'retrieval': '{"snapshot_url": null}'}
        kwargs = {'is_active_video': True, 'is_active_image': False,
                  'camera_type': 'non_ip', 'snapshot_url': None}

        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_stream(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": self.expected_cameraID,
        }
        mock_post.return_value = mock_response
        # validate result
        data = {'video_path': None, 'image_path': None, 'model': None, 'brand': None, 'port': None,
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo',
                'timezone_name': 'test_t_name', 'timezone_id': 'test_t_id', 'utc_offset': 3,
                'resolution_height': 480, 'resolution_width': 720, 'city': 'West Lafayette',
                'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'ip': None,
                'snapshot_url': None, 'is_active_video': True, 'is_active_image': False,
                'type': 'stream', 'retrieval': '{"m3u8_url": "test_m3u8"}'}

        kwargs = {'video_path': None, 'image_path': None, 'model': None, 'brand': None,
                  'port': None, 'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo',
                  'timezone_name': 'test_t_name', 'timezone_id': 'test_t_id', 'utc_offset': 3,
                  'resolution_height': 480, 'resolution_width': 720, 'city': 'West Lafayette',
                  'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                  'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                  'ip': None, 'snapshot_url': None, 'is_active_video': True,
                  'is_active_image': False, 'camera_type': 'stream', 'm3u8_url': 'test_m3u8'}
        resultID = self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(resultID, self.expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_kwrgs_missing_required(self, mock_post):

        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Format Error Messages",
        }
        mock_post.return_value = mock_response
        # validate result
        data = {'is_active_image': False, 'type': 'stream',
                'retrieval': '{"m3u8_url": null}'}
        kwargs = {'is_active_image': False, 'camera_type': 'stream'}

        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.get')
    def test_add_camera_expired_token_success(self, mock_get, mock_post):
        self.client.token = 'ExpiredToken'
        # set first request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Token expired.',
        }
        # set second request.post's result
        mock_response2 = mock.Mock()
        mock_response2.status_code = 201
        mock_response2.json.return_value = {
            'cameraID': self.expected_cameraID
        }
        mock_post.side_effect = [mock_response, mock_response2]
        # set _request_token()'s result
        mock_get_response = mock.Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'token': 'correctToken'
        }
        mock_get.return_value = mock_get_response
        # run the test

        kwargs = {'is_active_video': True, 'is_active_image': False, 'port': '8080',
                  'camera_type': 'ip', 'ip': '127.0.0.2', 'image_path': 'test_image_path',
                  'brand': 'test_brand', 'model': 'test_model',
                  'video_path': 'test_vid_path'}

        resultID = self.client.write_camera(**kwargs)

        self.assertEqual(resultID, self.expected_cameraID)
        mock_get.assert_called_with(self.token_url, params=self.token_params)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        data = {'is_active_video': True, 'is_active_image': False, 'type': 'ip',
                'retrieval': '{"brand": "test_brand", "image_path": "test_image_path",'
                             ' "ip": "127.0.0.2", "model": "test_model", "port": "8080",'
                             ' "video_path": "test_vid_path"}'}
        call_list = [mock.call(self.create_url, headers=headers, data=data),
                     mock.call(self.create_url, headers=self.header, data=data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('CAM2CameraDatabaseAPIClient.client.requests.post')
    def test_add_camera_internal_error(self, mock_post):
        # provide token for building header
        self.client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        # validate result
        data = {'is_active_video': True, 'is_active_image': False, 'type': 'ip',
                'retrieval': '{"brand": "test_brand", "image_path": "test_image_path",'
                             ' "ip": "127.0.0.2", "model": "test_model", "port": "8080",'
                             ' "video_path": "test_vid_path"}'}
        kwargs = {'is_active_video': True, 'is_active_image': False, 'camera_type': 'ip',
                  'ip': '127.0.0.2', 'port': '8080', 'brand': 'test_brand',
                  'model': 'test_model', 'image_path': 'test_image_path',
                  'video_path': 'test_vid_path'}
        with self.assertRaises(InternalError):
            self.client.write_camera(**kwargs)
        mock_post.assert_called_once_with(self.create_url, headers=self.header, data=data)
        self.assertEqual(0, mock_response.json.call_count)

    def test_write_camera_illegal_args(self):
        self.client.token = 'correctToken'

        kwargs = {'illegal': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                  'image_path': 'test_image_path', 'video_path': 'test_vid_path'}

        with self.assertRaises(FormatError):
            self.client.write_camera(**kwargs)

if __name__ == '__main__':
    unittest.main()
