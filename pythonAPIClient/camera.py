"""
Represents a camera.
"""

class Camera(object):

    """Class representing a general camera.


    Attributes
    ----------
    cameraID : str
        Id of the camera.
    legacy_cameraID : :obj:`int`, optional
        Id of the camera in previous CAM2 camera database.
    camera_type: str
        Type of the camera.
    source : :obj:`str`, optional
    country : :obj:`str`, optional
    state : :obj:`str`, optional
    city : :obj:`str`, optional
    longitude : :obj:`float`, optional
    latitude : :obj:`float`, optional
    is_active_image : :obj:`bool`, optional
    is_active_video : :obj:`bool`, optional
    resolution_width : :obj:`int`, optional
    resolution_height : :obj:`int`, optional
    utc_offset : :obj:`int`, optional
    timezone_id : :obj:`str`, optional
    timezont_name : :obj:`str`, optional
    reference_logo : :obj:`str`, optional
    reference_url : :obj:`str`, optional

    """

    def __init__(self, **dict_entries):
        """Client initialization method.

        Parameters
        ----------
        dict_entries: dict
            Dictionary of all field values of a camera.

        Note
        ----

            User should not construct any camera object on his/her own.

            Camera should only be initialized by results returned from the API.

            Documentation of camera constructor is for CAM2 API team only.

        """
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
    """Represent a single ip camera.

    This is a subclass of Camera.

    Attributes
    ----------
    ip : str
    port : str
    brand : :obj:`str`, optional
    model : :obj:`str`, optional
    image_path : :obj:`str`, optional
    video_path : :obj:`str`, optional

    """

class NonIPCamera(Camera):
    """Represent a single non-ip camera.

    This is a subclass of Camera.

    Attributes
    ----------
    snapshot_url : str
    
    """

class StreamCamera(Camera):
    """Represent a single stream camera.

    This is a subclass of Camera.

    Attributes
    ----------
    m3u8_url : str
    
    """
