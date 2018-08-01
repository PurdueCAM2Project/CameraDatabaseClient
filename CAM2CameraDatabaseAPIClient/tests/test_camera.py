"""
This class holds the code to test camera objects.
"""
import unittest
import sys
from os import path
from CAM2CameraDatabaseAPIClient.camera import Camera, IPCamera, NonIPCamera, StreamCamera

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class TestCamera(unittest.TestCase):

    def setUp(self):
        self.cam_attr = {
            'cameraID': 'test',
            'legacy_cameraID': 1,
            'camera_type': 'ip',
            'source': None,
            'country': 'USA',
            'state': 'IN',
            'city': None,
            'longitude': 50,
            'latitude': 50.0,
            'is_active_image': True,
            'is_active_video': False,
            'resolution_width': 1900,
            'resolution_height': 1000,
            'utc_offset': 8,
            'timezone_id': 0,
            'timezone_name': 'UTC',
            'reference_logo': None,
            'reference_url': None
        }

    def test_cam_init(self):
        cam = Camera(**self.cam_attr)
        self.assertTrue(isinstance(cam, Camera))
        self.assertTrue(isinstance(cam, dict))

    def test_non_ip_cam_init(self):
        non_ip_attr = {'snapshot_url': 'test_url'}
        self.cam_attr.update(non_ip_attr)
        non_ip_cam_test = NonIPCamera(**self.cam_attr)

        self.assertTrue(isinstance(non_ip_cam_test, NonIPCamera))
        self.assertTrue(isinstance(non_ip_cam_test, dict))
        self.assertTrue(issubclass(non_ip_cam_test.__class__, Camera))

        self.assertEqual(non_ip_cam_test, self.cam_attr)
        self.cam_attr.pop('snapshot_url')

    def test_stream_cam_init(self):
        stream_attr = {'m3u8_url': 'test_url'}
        self.cam_attr.update(stream_attr)
        stream_cam_test = StreamCamera(**self.cam_attr)

        self.assertTrue(isinstance(stream_cam_test, StreamCamera))
        self.assertTrue(isinstance(stream_cam_test, dict))
        self.assertTrue(issubclass(stream_cam_test.__class__, Camera))

        self.assertEqual(stream_cam_test, self.cam_attr)

        self.cam_attr.pop('m3u8_url')

    def test_non_ip_cam_init(self):
        ip_attr = dict(self.cam_attr)
        ip_attr.update({
            'ip': '127.0.0.1',
            'port': 80,
            'brand': 'test_brand',
            'model': 'test_model',
            'image_path': 'test_image',
            'video_path': None})

        ip_cam_test = IPCamera(**ip_attr)

        self.assertTrue(isinstance(ip_cam_test, IPCamera))
        self.assertTrue(isinstance(ip_cam_test, dict))
        self.assertTrue(issubclass(ip_cam_test.__class__, Camera))

        self.assertEqual(ip_cam_test, ip_attr)



if __name__ == '__main__':
    unittest.main()
