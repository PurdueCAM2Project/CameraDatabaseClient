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
        self.base_URL = 'http://localhost:8080/'

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
    def test_add_camera_ip(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "test_cameraID",
        }
        mock_post.return_value = mock_response
        # validate result
        expected_cameraID = 'test_cameraID'
        url = Client.base_URL + 'cameras/create'
        header = {'Authorization': 'Bearer correctToken'}
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': 'test_vid_path',
                'image_path': 'test_image_path', 'model': 'test_model', 'brand': 'test_brand', 'port': '8080',
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'ip': '127.0.0.2', 'is_active_video': True, 'is_active_image': False,
                'type': 'ip',
                'retrieval': '{\n    "brand":"test_brand",\n    "image_path":"test_image_path",\n    '
                             '"ip":"127.0.0.2",\n    "model":"test_model",\n    "port":"8080",\n    '
                             '"video_path":"test_vid_path"\n}'}

        resultID = client.add_camera(camera_type='ip', is_active_image=False, is_active_video=True, ip='127.0.0.2',
                                     snapshot_url=None, m3u8_url=None, legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url', port='8080', brand='test_brand', model='test_model',
                                     image_path='test_image_path', video_path='test_vid_path')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_add_camera_non_ip(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "test_cameraID",
        }
        mock_post.return_value = mock_response
        # validate result
        expected_cameraID = 'test_cameraID'
        url = Client.base_URL + 'cameras/create'
        header = {'Authorization': 'Bearer correctToken'}
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': None, 'image_path': None, 'model': None,
                'brand': None, 'port': None, 'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo',
                'timezone_name': 'test_t_name', 'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480,
                'resolution_width': 720, 'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA',
                'longitude': 'test_long', 'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                'm3u8_url': None, 'snapshot_url': 'test_snapshot', 'ip': None, 'is_active_video': True,
                'is_active_image': False, 'type': 'non-ip', 'retrieval': '{\n    "snapshot_url":"test_snapshot"\n}'}

        resultID = client.add_camera(camera_type='non-ip', is_active_image=False, is_active_video=True,
                                     snapshot_url='test_snapshot', m3u8_url=None, legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_add_camera_stream(self, mock_post):
        clientId = '0' * 96
        clientSecret = '0' * 71
        client = Client(clientId, clientSecret)
        # provide token for building header
        client.token = "correctToken"
        # manipulate request.post's result
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "cameraID": "test_cameraID",
        }
        mock_post.return_value = mock_response
        # validate result
        expected_cameraID = 'test_cameraID'
        url = Client.base_URL + 'cameras/create'
        header = {'Authorization': 'Bearer correctToken'}
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': None, 'image_path': None, 'model': None,
                'brand': None, 'port': None, 'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo',
                'timezone_name': 'test_t_name', 'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480,
                'resolution_width': 720, 'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA',
                'longitude': 'test_long', 'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0,
                'm3u8_url': 'test_m3u8', 'snapshot_url': None, 'ip': None, 'is_active_video': True,
                'is_active_image': False, 'type': 'non-ip', 'retrieval': '{\n    "snapshot_url":null\n}'}

        resultID = client.add_camera(camera_type='non-ip', is_active_image=False, is_active_video=True,
                                     snapshot_url=None, m3u8_url='test_m3u8', legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(resultID, expected_cameraID)
        self.assertEqual(1, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    @mock.patch('pythonAPIClient.client.requests.get')
    def test_add_camera_expired_token_success(self, mock_get, mock_post):
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
            'cameraID': 'test_cameraID'
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
        resultID = client.add_camera(camera_type='ip', is_active_image=False, is_active_video=True, ip='127.0.0.2',
                                     snapshot_url=None, m3u8_url=None, legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url', port='8080', brand='test_brand', model='test_model',
                                     image_path='test_image_path', video_path='test_vid_path')
        self.assertEqual(resultID, 'test_cameraID')
        mock_get.assert_called_with(self.base_URL + 'auth/?clientID=' + clientId +
                                    '&clientSecret=' + clientSecret)
        headers = {'Authorization': 'Bearer ExpiredToken'}
        newheaders = {'Authorization': 'Bearer newToken'}
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': 'test_vid_path',
                'image_path': 'test_image_path', 'model': 'test_model', 'brand': 'test_brand', 'port': '8080',
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'ip': '127.0.0.2', 'is_active_video': True, 'is_active_image': False,
                'type': 'ip',
                'retrieval': '{\n    "brand":"test_brand",\n    "image_path":"test_image_path",\n    '
                             '"ip":"127.0.0.2",\n    "model":"test_model",\n    "port":"8080",\n    '
                             '"video_path":"test_vid_path"\n}'}
        call_list = [mock.call(self.base_URL + 'cameras/create', headers=headers, data=data),
                     mock.call(self.base_URL + 'cameras/create', headers=newheaders, data=data)]
        self.assertEqual(mock_post.call_args_list, call_list)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_add_camera_internal_error(self, mock_post):
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
        url = Client.base_URL + 'cameras/create'
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': 'test_vid_path',
                'image_path': 'test_image_path', 'model': 'test_model', 'brand': 'test_brand', 'port': '8080',
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'ip': '127.0.0.2', 'is_active_video': True, 'is_active_image': False,
                'type': 'ip',
                'retrieval': '{\n    "brand":"test_brand",\n    "image_path":"test_image_path",\n    '
                             '"ip":"127.0.0.2",\n    "model":"test_model",\n    "port":"8080",\n    '
                             '"video_path":"test_vid_path"\n}'}
        header = {'Authorization': 'Bearer correctToken'}

        with self.assertRaises(InternalError):
            client.add_camera(camera_type='ip', is_active_image=False, is_active_video=True, ip='127.0.0.2',
                                     snapshot_url=None, m3u8_url=None, legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url', port='8080', brand='test_brand', model='test_model',
                                     image_path='test_image_path', video_path='test_vid_path')
        mock_post.assert_called_once_with(url, headers=header, data=data)
        self.assertEqual(0, mock_response.json.call_count)

    @mock.patch('pythonAPIClient.client.requests.post')
    def test_add_camera_all_correct_Format_Error(self, mock_post):
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
        mock_post.return_value = mock_response
        url = self.base_URL + 'cameras/create'
        data = {'url': 'http://localhost:8080/cameras/create', 'video_path': 'test_vid_path',
                'image_path': 'test_image_path', 'model': 'test_model', 'brand': 'test_brand', 'port': '8080',
                'reference_url': 'test_ref_url', 'reference_logo': 'test_ref_logo', 'timezone_name': 'test_t_name',
                'timezone_id': 'test_t_id', 'utc_offset': 3, 'resolution_height': 480, 'resolution_width': 720,
                'city': 'West Lafayette', 'state': 'Indiana', 'country': 'USA', 'longitude': 'test_long',
                'latitude': 'test_lad', 'source': 'test_source', 'legacy_cameraID': 0, 'm3u8_url': None,
                'snapshot_url': None, 'ip': '127.0.0.2', 'is_active_video': True, 'is_active_image': False,
                'type': 'ip',
                'retrieval': '{\n    "brand":"test_brand",\n    "image_path":"test_image_path",\n    '
                             '"ip":"127.0.0.2",\n    "model":"test_model",\n    "port":"8080",\n    '
                             '"video_path":"test_vid_path"\n}'}
        with self.assertRaises(FormatError):
            client.add_camera(camera_type='ip', is_active_image=False, is_active_video=True, ip='127.0.0.2',
                                     snapshot_url=None, m3u8_url=None, legacy_cameraID=000000000,
                                     source='test_source', latitude='test_lad', longitude='test_long', country='USA',
                                     state='Indiana', city='West Lafayette', resolution_width=720,
                                     resolution_height=480, utc_offset=3, timezone_id='test_t_id',
                                     timezone_name='test_t_name', reference_logo='test_ref_logo',
                                     reference_url='test_ref_url', port='8080', brand='test_brand', model='test_model',
                                     image_path='test_image_path', video_path='test_vid_path')
        mock_post.assert_called_once_with(url, headers={'Authorization': 'Bearer CorrectToken'}, data=data)
        self.assertEqual(1, mock_response.json.call_count)

if __name__ == '__main__':
    unittest.main()
