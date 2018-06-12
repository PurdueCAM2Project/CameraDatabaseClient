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
    
    def test_cam_init_all_fields(self):
        cam = Camera("ip", True, True, 1, 'test_cameraID', "test_source", 10, 50, "test_country", "test_state","test_city", 1
                , 1, 0,0,"", "", "test_url")
        self.assertEqual(cam.state, 'test_state')

        ip_cam_test1 = IPCamera("ip", True, True, 'test_ip', 1, 'test_cameraID', "test_source", 10, 50, "test_country", "test_state", "test_city"
                                , 1, 1, None, None, None, None, "test_url", "test_ip_port",
                                "test_brand", "test_model"
                                , "test_image_path", "test_video_path")
        self.assertEqual(ip_cam_test1.video_path, 'test_video_path')
        ip_cam_test2 = IPCamera("ip", True, True, 'test_ip', 1, 'test_cameraID', 10, 50, "test_country", "test_state", "test_city"
                                , 1, 1, None, None, None, None, "test_url", "test_ip_port",
                                "test_brand", "test_model"
                                , "test_image_path", None)
        self.assertIsNone(ip_cam_test2.video_path)

        non_ip_cam_test1 = NonIPCamera("non_ip", True, True, 'test_snapshot_url', 1, 'test_cameraID', "test_source", 10, 50, "test_country", "test_state", "test_city"
                                       , 1, 1, None, None, None, None, "test_url")
        self.assertEqual(non_ip_cam_test1.snapshot_url, 'test_snapshot_url')

        stream_cam_test1 = StreamCamera("stream", True, True, 'test_m3u8_url', 1, 'test_cameraID', "test_source", 10, 50, "test_country", "test_state", "test_city"
                                        , 1, 1, None, None, None, None, "test_url")
        self.assertEqual(stream_cam_test1.m3u8_url, 'test_m3u8_url')


        self.assertTrue(isinstance(cam, Camera))

        self.assertTrue(isinstance(ip_cam_test1, IPCamera) and issubclass(ip_cam_test1.__class__, cam.__class__))
        self.assertTrue(isinstance(ip_cam_test2, IPCamera) and issubclass(ip_cam_test2.__class__, cam.__class__))

        self.assertTrue(isinstance(non_ip_cam_test1, NonIPCamera) and issubclass(non_ip_cam_test1.__class__, cam.__class__))

        self.assertTrue(isinstance(stream_cam_test1, StreamCamera) and issubclass(stream_cam_test1.__class__, cam.__class__))

    def test_cam_init_only_required_fields(self):
        cam = Camera(camera_type='ip', is_active_image=False, is_active_video=True)
        self.assertEqual(cam.camera_type, 'ip')
        self.assertTrue(cam.is_active_video)

        ip_cam_test1 = IPCamera(ip='test_ip', camera_type='ip', is_active_image=False, is_active_video=True)
        self.assertIsNone(ip_cam_test1.video_path)
        self.assertEqual(ip_cam_test1.ip, 'test_ip')

        non_ip_cam_test1 = NonIPCamera(camera_type='non_ip', is_active_image=False, snapshot_url='test_snapshot_url', is_active_video=True)
        self.assertEqual(non_ip_cam_test1.snapshot_url, 'test_snapshot_url')
        self.assertIsNone(non_ip_cam_test1.cameraID)

        stream_cam_test1 = StreamCamera(camera_type='stream', is_active_image=False, is_active_video=True, m3u8_url='test_m3u8_url')
        self.assertEqual(stream_cam_test1.m3u8_url, 'test_m3u8_url')
        self.assertIsNone(stream_cam_test1.legacy_cameraID)

        self.assertTrue(isinstance(cam, Camera))

        self.assertTrue(isinstance(ip_cam_test1, IPCamera) and issubclass(ip_cam_test1.__class__, cam.__class__))

        self.assertTrue(isinstance(non_ip_cam_test1, NonIPCamera) and issubclass(non_ip_cam_test1.__class__, cam.__class__))

        self.assertTrue(isinstance(stream_cam_test1, StreamCamera) and issubclass(stream_cam_test1.__class__, cam.__class__))

    def test_cam_init_missing_required_fields(self):

        with self.assertRaises(TypeError):
            cam = Camera(is_active_image=False, is_active_video=True)
        with self.assertRaises(TypeError):
            cam = Camera(camer_type='non_ip', is_active_video=True)
        with self.assertRaises(TypeError):
            cam = Camera(camer_type='non_ip', is_active_image=True)

        with self.assertRaises(TypeError):
            ip_cam_test1 = IPCamera(camera_type='ip', is_active_image=False, is_active_video=True)

        with self.assertRaises(TypeError):
            non_ip_cam_test1 = NonIPCamera(camera_type='non_ip', is_active_image=False, is_active_video=True)

        with self.assertRaises(TypeError):
            stream_cam_test1 = StreamCamera(camera_type='stream', is_active_image=False, is_active_video=True)

if __name__ == '__main__':
    unittest.main()

