import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera
from pythonAPIClient.client import Client
from pythonAPIClient.error import Error

class TestCamera(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_cam_init(self):
        cam = Camera('dummy')
        self.assertTrue(isinstance(cam, Camera))

        ip_cam = IPCamera('dummy')
        self.assertTrue(isinstance(ip_cam, IPCamera) and issubclass(ip_cam.__class__, cam.__class__))

        non_ip_cam = NonIPCamera('dummy')
        self.assertTrue(isinstance(non_ip_cam, NonIPCamera) and issubclass(non_ip_cam.__class__, cam.__class__))

        stream_cam = StreamCamera('dummy')
        self.assertTrue(isinstance(stream_cam, StreamCamera) and issubclass(stream_cam.__class__, cam.__class__))


if __name__ == '__main__':
    unittest.main()