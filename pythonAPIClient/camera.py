class Camera(object):
    """
    Represent a single camera
    """
    # TODO: define attributes and constructor of basic camera object
    # replace others with desired field names
    def __init__(self, others):
        pass

class IPCamera(Camera):
    """
    Represent a single ip_camera
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of ip camera object
    # replace others with desired field names
    def __init__(self, others):
        super(IPCamera, self).__init__()

class NonIPCamera(Camera):
    """
    Represent a non-IP camera.
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of non_ip camera object
    # replace others with desired field names
    def __init__(self,others):
        super(NonIPCamera, self).__init__()

class StreamCamera(Camera):
    """
    Represent a Stream camera.
    This is a subclass of Camera
    """
    # TODO: define extra retrieval attributes and constructor of stream camera object
    # replace others with desired field names
    def __init__(self,others):
        super(StreamCamera, self).__init__()