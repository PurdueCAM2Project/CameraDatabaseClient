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
        url = self.base_URL + 'cameras/search'
        with self.assertRaises(TypeError):
            client.search_camera(country='USA')
        mock_get.assert_called_with(url, headers={'Authorization': 'Bearer correctToken'},
                                    params={'country': 'USA'})
        self.assertEqual(2, mock_get.call_count)

    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct_Expired_Token(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
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
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'CorrectToken'
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        url = self.base_URL + 'cameras/search'
        with self.assertRaises(InternalError):
            client.search_camera(country='USA')
        mock_get.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'},
                                         params={'country': 'USA'})
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
        url = self.base_URL + 'cameras/search'
        with self.assertRaises(FormatError):
            client.search_camera(resolution_width='USA')
        mock_get.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'},
                                         params={'resolution_width': 'USA'})
        self.assertEqual(1, mock_response.json.call_count)


    @mock.patch('pythonAPIClient.client.requests.get')
    def test_search_camera_all_correct(self, mock_get):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        client.token = 'CorrectToken'
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
        response_dict = client.search_camera(
            country='JP', camera_type='non_ip', is_active_image=True, offset=100)
        url = self.base_URL + 'cameras/search'
        mock_get.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'},
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
        self.assertEqual(response_dict[0].__dict__, actual_dict,
                         'Returned json is not tranlated correctly')
        return response_dict

if __name__ == '__main__':
    unittest.main()
