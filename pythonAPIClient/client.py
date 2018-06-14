"""
Represents a CAM2 client application.
"""
import requests
from .error import Error, AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError
from .camera import Camera, IPCamera, NonIPCamera, StreamCamera

"""
Represent a CAM2 client application.
"""


class Client(object):
    # Static variable to store the base URL.
    base_URL = 'https://cam2-api.herokuapp.com/'
    """
    Represent a CAM2 client application.
    """

    """
    Represent a CAM2 client application.
    """
    def request_token(self):
        url = Client.base_URL + 'auth/?clientID=' + self.clientId + \
              '&clientSecret=' + self.clientSecret
        response = requests.get(url)
        if response.status_code == 200:
            self.token = response.json()['token']
        elif response.status_code == 404:
            raise ResourceNotFoundError(response.json()['message'])
        elif response.status_code == 401:
            raise AuthenticationError(response.json()['message'])
        else:
            raise InternalError()

    """
    Represent a CAM2 client application.
    """
    def header_builder(self):
        head = {'Authorization': 'Bearer ' + str(self.token)}
        return head

    """
    Represent a CAM2 client application.
    """
    def __init__(self, clientId, clientSecret):
        # clientId are of a fixed length of 96 characters.
        if len(clientId) != 96:
            raise InvalidClientIdError
        # clientSecret are of a fixed length of 71 characters.
        if len(clientSecret) != 72:
            raise InvalidClientSecretError
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.token = None

    """
    Functions for webUI
    # TODO: return clientID and client secret
    """
    def register(self, owner, permissionLevel='user'):
        pass

    """
    Represent a CAM2 client application.
    # TODO: update client's owner
    """
    def update_owner(self, clientID, owner):
        pass

    """
    Represent a CAM2 client application.
    # TODO: update client's permissionLevel
    """
    def update_permission(self, clientID, permissionLevel):
        pass

    """
    Represent a CAM2 client application.
    # TODO: get clientID by owner
    """
    def client_ids_by_owner(self, owner):
        pass

    """
    Represent a CAM2 client application.
    # TODO: get api usage count by client
    """
    def usage_by_client(self, clientID):
        pass

    """
    Function for admin
    # TODO: add a camera to database
    """
    def add_camera(self, Camera):
        pass

    """
    Function for admin
    # TODO: update a camera in database
    # replace others with desired field names
    """
    def update_camera(self, camID, others):
        pass

    """
    Function for user
    # TODO: get a camera
    """
    def camera_by_id(self, cameraID):
        pass

    """
    Function for user
    # TODO: fix the commenting 
    """
    def search_camera(self, latitude=None, longitude=None, radius=None, type=None, source=None,
                      country=None, state=None, city=None, resolution_width=None,
                      resolution_heigth=None, is_active_image=None, is_active_video=None,
                      offset=None):
        if self.token is None:
            self.request_token()
        url = Client.base_URL + 'cameras/search?'
        if latitude is not None:
            url += 'lat=' + latitude + '&'
        if longitude is not None:
            url += 'lng=' + longitude + '&'
        if radius is not None:
            url += 'radius=' + radius + '&'
        if type is not None:
            url += 'type=' + type + '&'
        if source is not None:
            url += 'source=' + source + '&'
        if country is not None:
            url += 'country=' + country + '&'
        if state is not None:
            url += 'state=' + state + '&'
        if city is not None:
            url += 'city=' + city + '&'
        if resolution_width is not None:
            url += 'resolution_width=' + resolution_width + '&'
        if resolution_heigth is not None:
            url += 'resolution_heigth=' + resolution_heigth + '&'
        if is_active_image is not None:
            url += 'is_active_image=' + is_active_image + '&'
        if is_active_video is not None:
            url += 'is_active_video=' + is_active_video + '&'
        if offset is not None:
            url += 'offset=' + offset + '&'
        url = url[:-1]
        response = requests.get(url, headers=self.header_builder())
        if response.status_code == 401:
            self.request_token()
            response = requests.get(url, headers=self.header_builder())
        elif response.status_code == 422:
            raise FormatError(response.json()['message'])
        elif response.status_code == 500:
            raise InternalError()
        camera_response_array = response.json()
        camera_processed = []
        for x in range(len(camera_response_array)):
            current_object = camera_response_array[x]
            if current_object['type'] == 'ip':
                camera_processed.append(IPCamera(current_object['cameraID'],
                                                 current_object['type'],
                                                 current_object['source'],
                                                 current_object['latitude'],
                                                 current_object['longitude'],
                                                 current_object['country'],
                                                 current_object['state'],
                                                 current_object['city'],
                                                 current_object['resolution_width'],
                                                 current_object['resolution_height'],
                                                 current_object['is_active_image'],
                                                 current_object['is_active_video'],
                                                 current_object['utc_offset'],
                                                 current_object['timezone_id'],
                                                 current_object['timezone_name'],
                                                 current_object['reference_logo'],
                                                 current_object['reference_url'],
                                                 current_object['retrieval']['ip'],
                                                 current_object['retrieval']['port'],
                                                 current_object['retrieval']['brand'],
                                                 current_object['retrieval']['model'],
                                                 current_object['retrieval']['image_path'],
                                                 current_object['retrieval']['video_path']))
            elif current_object['type'] == 'non_ip':
                camera_processed.append(NonIPCamera(current_object['cameraID'],
                                                    current_object['type'],
                                                    current_object['source'],
                                                    current_object['latitude'],
                                                    current_object['longitude'],
                                                    current_object['country'],
                                                    current_object['state'],
                                                    current_object['city'],
                                                    current_object['resolution_width'],
                                                    current_object['resolution_height'],
                                                    current_object['is_active_image'],
                                                    current_object['is_active_video'],
                                                    current_object['utc_offset'],
                                                    current_object['timezone_id'],
                                                    current_object['timezone_name'],
                                                    current_object['reference_logo'],
                                                    current_object['reference_url'],
                                                    current_object['retrieval']['snapshot_url']))
            else:
                camera_processed.append(StreamCamera(current_object['cameraID'],
                                                     current_object['type'],
                                                     current_object['source'],
                                                     current_object['latitude'],
                                                     current_object['longitude'],
                                                     current_object['country'],
                                                     current_object['state'],
                                                     current_object['city'],
                                                     current_object['resolution_width'],
                                                     current_object['resolution_height'],
                                                     current_object['is_active_image'],
                                                     current_object['is_active_video'],
                                                     current_object['utc_offset'],
                                                     current_object['timezone_id'],
                                                     current_object['timezone_name'],
                                                     current_object['reference_logo'],
                                                     current_object['reference_url'],
                                                     current_object['retrieval']['m3u8_url']))
        return camera_processed
        pass
