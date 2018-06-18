"""
Represents a camera.
"""

class Camera(object):
    """
    Represent a general camera.
    This class includes fields common for all types of camera.
    """

    def __init__(self, **dict_entries):
        self.__dict__.update(dict_entries)

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def process_json(**dict_entries):
        dict_entries['camera_type'] = dict_entries['type']
        dict_entries.pop('type', None)
        dict_entries.update(dict_entries['retrieval'])
        dict_entries.pop('retrieval', None)

        if dict_entries['camera_type'] == 'ip':
            return IPCamera(**dict_entries)
        if dict_entries['camera_type'] == 'non_ip':
            return NonIPCamera(**dict_entries)
        return StreamCamera(**dict_entries)

class IPCamera(Camera):
    """
    Represent a single ip_camera.
    This is a subclass of Camera.
    """

class NonIPCamera(Camera):
    """
    Represent a non-IP camera.
    This is a subclass of Camera.
    """

class StreamCamera(Camera):
    """
    Represent a Stream camera.
    This is a subclass of Camera
    """
