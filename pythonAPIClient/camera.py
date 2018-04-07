class Camera(object):
    """
    Represent a single camera
    """
    # TODO: define attributes and constructor of basic camera object
    # replace others with desired field names
    def __init__(self, cameraID, type, source, lat, lng, country, state, city, resolution_width
                , resolution_height, is_active_image, is_active_video, utc_offset, timezone_id
                , timezone_name, reference_logo, reference_url):
        self.cameraId=cameraID;
        self.type=type;
        self.source=source;
        self.lat=lat;
        self.lng=lng;
        self.country=country;
        self.state=state;
        self.city=city;
        self.resolution_width=resolution_width;
        self.resolution_height=resolution_height;
        self.is_active_image=is_active_image;
        self.is_active_video=is_active_video;
        self.utc_offset=utc_offset;
        self.timezone_id=timezone_id;
        self.timezone_name=timezone_name;
        self.reference_logo=reference_logo;
        self.reference_url=reference_url;

class IPCamera(Camera):
    """
    Represent a single ip_camera
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of ip camera object
    # replace others with desired field names
    def __init__(self, ip,port,brand,model,image_path,video_path):
        super(IPCamera, self).__init__(ip,port,brand,model,image_path,video_path)
        self.ip=ip
        self.port=port
        self.brand=brand
        self.model=model
        self.image_path=image_path
        self.video_path=video_path

class NonIPCamera(Camera):
    """
    Represent a non-IP camera.
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of non_ip camera object
    # replace others with desired field names
    def __init__(self,snapshot_url):
        super(NonIPCamera, self).__init__(snapshot_url)
        self.snapshot_url=snapshot_url

class StreamCamera(Camera):
    """
    Represent a Stream camera.
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of stream camera object
    # replace others with desired field names
    def __init__(self,m3u8_url):
        super(StreamCamera, self).__init__(m3u8_url)
        self.m3u8_url=m3u8_url