class Camera(object):
    """
    Represent a single camera
    """

    def __init__(self, camera_type, is_active_image, is_active_video, legacy_cameraID=None
                , cameraID=None, source=None, lat=None, lng=None, country=None, state=None, city=None
                , resolution_width=None, resolution_height=None, utc_offset=None, timezone_id=None
                , timezone_name=None, reference_logo=None, reference_url=None):
        self.cameraID=cameraID
        self.legacy_cameraID=legacy_cameraID
        self.camera_type=camera_type
        self.source=source
        self.lat=lat
        self.lng=lng
        self.country=country
        self.state=state
        self.city=city
        self.resolution_width=resolution_width
        self.resolution_height=resolution_height
        self.is_active_image=is_active_image
        self.is_active_video=is_active_video
        self.utc_offset=utc_offset
        self.timezone_id=timezone_id
        self.timezone_name=timezone_name
        self.reference_logo=reference_logo
        self.reference_url=reference_url

class IPCamera(Camera):
    """
    Represent an IP camera
    This is a subclass of Camera
    """

    def __init__(self, camera_type, is_active_image, is_active_video, ip, legacy_cameraID=None
                , cameraID=None, source=None, lat=None, lng=None, country=None, state=None, city=None
                , resolution_width=None, resolution_height=None, utc_offset=None, timezone_id=None
                , timezone_name=None, reference_logo=None, reference_url=None
                , port=80, brand=None, model=None, image_path=None, video_path=None):
                self.ip = ip
                self.port = port
                self.brand = brand
                self.model = model
                self.image_path = image_path
                self.video_path = video_path
                super(IPCamera, self).__init__(cameraID, camera_type, source, lat, lng, country, state, city, resolution_width
                , resolution_height, is_active_image, is_active_video, utc_offset, timezone_id
                , timezone_name, reference_logo, reference_url)

class NonIPCamera(Camera):
    """
    Represent a Non-IP camera.
    This is a subclass of Camera
    """

    def __init__(self, camera_type, is_active_image, is_active_video, snapshot_url, legacy_cameraID=None
                , cameraID=None, source=None, lat=None, lng=None, country=None, state=None, city=None
                , resolution_width=None, resolution_height=None, utc_offset=None, timezone_id=None
                , timezone_name=None, reference_logo=None, reference_url=None):
                self.snapshot_url=snapshot_url
                super(NonIPCamera, self).__init__(cameraID, camera_type, source, lat, lng, country, state, city, resolution_width
                , resolution_height, is_active_image, is_active_video, utc_offset, timezone_id
                , timezone_name, reference_logo, reference_url)

class StreamCamera(Camera):
    """
    Represent a Stream camera.
    This is a subclass of Camera
    """

    def __init__(self, camera_type, is_active_image, is_active_video, m3u8_url, legacy_cameraID=None
                , cameraID=None, source=None, lat=None, lng=None, country=None, state=None, city=None
                , resolution_width=None, resolution_height=None, utc_offset=None, timezone_id=None
                , timezone_name=None, reference_logo=None, reference_url=None):
                self.m3u8_url = m3u8_url
                super(StreamCamera, self).__init__(cameraID, camera_type, source, lat, lng, country, state, city, resolution_width
                        , resolution_height, is_active_image, is_active_video, utc_offset, timezone_id
                        , timezone_name, reference_logo, reference_url)
