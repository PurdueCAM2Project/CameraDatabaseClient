import unittest
import sys
from os import path
from pythonAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class TestCamera(unittest.TestCase):

    def setUp(self):
        pass

    def test_cam_init(self):
        cam = Camera(1, "ip", "test_source", 10, 50, "test_country", "test_state", "test_city", 1,
                     1, 0, 0, "", "",
                     "", "null", "test_url")

        ip_cam_test1 = IPCamera(1, "ip", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                1, 1, 0, 0, "null", "null", "null", "null", "test_url", "ip", "test_ip_port",
                                "test_brand", "test_model", "test_image_path", "test_video_path")
        ip_cam_test2 = IPCamera(1, "ip", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                1, 1, 0, 0, "null", "null", "null", "null", "test_url", "ip", "test_ip_port",
                                "test_brand", "test_model", "test_image_path", None)

        non_ip_cam_test1 = NonIPCamera(1, "nonip", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                       1, 1, 0, 0, "null", "null", "null", "null", "test_url", "test_snapshot_url")
        non_ip_cam_test2 = NonIPCamera(1, "nonip", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                       1, 1, 0, 0, "null", "null", "null", "null", "test_url", None)

        stream_cam_test1 = StreamCamera(1, "stream", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                        1, 1, 0, 0, "null", "null", "null", "null", "test_url", "test_m3u8_url")
        stream_cam_test2 = StreamCamera(1, "stream", "test_source", 10, 50, "test_country", "test_state", "test_city",
                                        1, 1, 0, 0, "null", "null", "null", "null", "test_url", None)

        self.assertTrue(isinstance(cam, Camera))

        self.assertTrue(isinstance(ip_cam_test1, IPCamera) and issubclass(ip_cam_test1.__class__, cam.__class__))
        self.assertTrue(isinstance(ip_cam_test2, IPCamera) and issubclass(ip_cam_test2.__class__, cam.__class__))

        self.assertTrue(
            isinstance(non_ip_cam_test1, NonIPCamera) and issubclass(non_ip_cam_test1.__class__, cam.__class__))
        self.assertTrue(
            isinstance(non_ip_cam_test2, NonIPCamera) and issubclass(non_ip_cam_test2.__class__, cam.__class__))

        self.assertTrue(
            isinstance(stream_cam_test1, StreamCamera) and issubclass(stream_cam_test1.__class__, cam.__class__))
        self.assertTrue(
            isinstance(stream_cam_test2, StreamCamera) and issubclass(stream_cam_test2.__class__, cam.__class__))


if __name__ == '__main__':
    unittest.main()
