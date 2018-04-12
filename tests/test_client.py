import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
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

        client = Client('dummyID', 'dummySecret', 'dummyToken')
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.id, 'dummyID', 'ID not stored in the client object.')
        self.assertEqual(client.secret, 'dummySecret', 'Secret not stored in the client object.')
        self.assertEqual(client.token, 'dummyToken', 'Token not stored in the client object')
    
    def test_build_header(self):
        self.assertEqual(Client.header_builder('dummyToken'), 'dummy')

    def test_get_token(self):
        self.assertEqual(Client.request_token('dummyID', 'dummySecret'), 'dummy')


if __name__ == '__main__':
    unittest.main()   