"""
Represents a CAM2 client application.
"""
import requests
import json
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError
from .camera import IPCamera, NonIPCamera, StreamCamera


class Client(object):
    # Static variable to store the base URL.
    #base_URL = 'https://cam2-api.herokuapp.com/'
    base_URL = 'http://localhost:8080/'
    """
    Represent a CAM2 client application.2323232
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

    def header_builder(self):
        head = {'Authorization': 'Bearer ' + str(self.token)}
        return head

    def __init__(self, clientId, clientSecret):
        """"
        #clientId are of a fixed length of 96 characters.
        if len(id) != 96:
            raise InvalidClientIdError
        # clientSecret are of a fixed length of 71 characters.
        if len(clientSecret) != 72:
            raise InvalidClientSecretError

        self.clientId = clientId
        self.clientSecret = clientSecret
        self.token = None

        """
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.token = None
    """
    Functions for webUI
    """
    # TODO: return clientID and client secret
    def register(self, owner, permissionLevel='user'):
        pass

    # TODO: update client's owner
    def update_owner(self, clientID, owner):
        pass

    # TODO: update client's permissionLevel
    def update_permission(self, clientID, permissionLevel):
        pass

    # TODO: get clientID by owner
    def client_ids_by_owner(self, owner):
        pass

    # TODO: get api usage count by client
    def usage_by_client(self, clientID):
        pass

    # TODO: add a camera to database
    def add_camera(self, camera_type, is_active_image, is_active_video, snapshot_url, m3u8_url, ip, legacy_cameraID=None,
                   source=None, lat=None, lng=None, country=None, state=None, city=None, resolution_width=None,
                   resolution_height=None, utc_offset=None, timezone_id=None, timezone_name=None, reference_logo=None,
                   reference_url=None, port=None, brand=None, model=None, image_path=None, video_path=None):

        url = Client.base_URL + 'cameras/create'
        if self.token is None:
           self.request_token()
        local_params = dict(locals())
        del local_params['self']
        local_params['type'] = local_params.pop('camera_type')
        if camera_type == 'ip':
            local_params['retrieval'] = {
                'ip': ip,
                'port': port,
                'brand': brand,
                'model': model,
                'image_path': image_path,
                'video_path': video_path
            }

        local_params['retrieval'] = json.dumps(local_params['retrieval'], sort_keys=True, indent=4, separators=(',', ':'))

        response = requests.post(url, headers=self.header_builder(), data=local_params)
        if response.status_code == 401:
            self.request_token()
            response = requests.get(url, headers=self.header_builder())
            print(response.json()['401 Err'])

    # TODO: update a camera in database
    # replace others with desired field names
    def update_camera(self, camID, others):
        pass

    # TODO: get a camera
    def camera_by_id(self, cameraID):
        pass

    def search_camera(self, latitude=None, longitude=None, radius=None, camera_type=None,
                      source=None, country=None, state=None, city=None, resolution_width=None,
                      resolution_height=None, is_active_image=None, is_active_video=None,
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
        if camera_type is not None:
            url += 'type=' + camera_type + '&'
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
        if resolution_height is not None:
            url += 'resolution_heigth=' + resolution_height + '&'
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
        for x in enumerate(camera_response_array):
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
