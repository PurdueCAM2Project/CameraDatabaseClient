"""
Represents a CAM2 client application.
"""
import requests
import json
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError, \
    AuthorizationError, ResourceConflictError
from .camera import Camera


class Client(object):
    """Class representing a CAM2 client application.

    [More detailed description of what client object do.]


    Attributes
    ----------
    clientId : str
        Id of the client application.
    clientSecret : str
        Secret of the client application.
    token : str
        Token for the client to access the CAM2 database.
        Each token expires in 5 minutes.

        [User does not need to provide this attribute]

    Note
    ----

        In order to access the package, register a new application by contacting the CAM2 team
        at https://www.cam2project.net/.

        For each methods except internal method like _check_token(),
        those methods will rerun request_token() to get a new token if token expires.
        But if the requests get status code of 401 for more than 2 times,
        we raise an Authentication error.

    """

    base_URL = 'https://cam2-api.herokuapp.com/'

    """str: Static variable to store the base URL.

    This is the URL of CAM2 Database API. User is able to send API calls directly to this URL.

    """

    def _check_token(self, response, flag, url, data=None, params=None):
        counter = 0
        while response.status_code == 401 and \
                response.json()['message'] == 'Token expired' and counter < 2:
            self.request_token()
            header = self.header_builder()
            if flag == 'GET':
                response = requests.get(url, headers=header, params=params)
            elif flag == 'POST':
                response = requests.post(url, headers=header, data=data)
            else:
                response = requests.put(url, headers=header, data=data)
            counter += 1
        return response

    def request_token(self):

        """A method to request an access token for the client application.
        Raises
        ------
        ResourceNotFoundError
            If no client app exists with the clientID of this client object.
        AuthenticationError
            If the client secret of this client object does not match the clientID.
        InternalError
            If there is an API internal error.
        """

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

        """Client initialization method.

        Parameters
        ----------
        clientId : str
            Id of the client application.
        clientSecret : str
            Secret of the client application.

        Raises
        ------
        InvalidClientIdError
            If the clientID is not in the correct format.
            ClientID should have a fixed length of 96 characters.
        InvalidClientSecretError
            If the client secret is not in the correct format.
            Client secret should have a length of at least 71 characters.

        """
        if len(clientId) != 96:
            raise InvalidClientIdError
        if len(clientSecret) < 71:
            raise InvalidClientSecretError
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.token = None

    # Functions for webUI

    def register(self, owner, permissionLevel='user'):
        """Client initialization method.

        Parameters
        ----------
        owner : str
            Username of the owner of the client application.
        permissionLevel : str, optional
            Permission level of the owner of the client application.
            Default permission level is 'user'.


        Returns
        -------
        str
            Client id of the newly registered client application.
        str
            Client secret of the newly registered client application.

        """
        url = Client.base_URL + 'apps/register'
        if self.token is None:
            self.request_token()
        header = self.header_builder()
        data = {'owner': owner, 'permissionLevel': permissionLevel}
        response = self._check_token(response=requests.post(url, headers=header, data=data),
                                     flag='POST', url=url, data=data)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()
        return response.json()['clientID'], response.json()['clientSecret']


    # TODO: update client's owner
    def update_owner(self, clientID, owner):
        """
        Parameters
        ----------
        clientID : str
            Client Id of the application.

        owner : str, optional
            (Optional) Username of owner.

        Returns
        -------
        str
            Success message.

        """
        url = Client.base_URL + 'apps/' + clientID
        if self.token is None:
            self.request_token()
        header = self.header_builder()
        data = {'owner': owner}
        response = self._check_token(response=requests.put(url, headers=header, data=data),
                                     flag='PUT', url=url, data=data)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            else:
                raise InternalError()
        return response.json()['message']

    # TODO: update client's permissionLevel
    def update_permission(self, clientID, permissionLevel):
        """
        Parameters
        ----------
        clientID : str
            Client Id of the application.

        permissionLevel : str, optional
            Permission level of client.

        Returns
        -------
        str
            Success message.

        """
        url = Client.base_URL + 'apps/' + clientID
        if self.token is None:
            self.request_token()
        header = self.header_builder()
        data = {'permissionLevel': permissionLevel}
        response = self._check_token(response=requests.put(url, headers=header, data=data),
                                     flag='PUT', url=url, data=data)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            else:
                raise InternalError()
        return response.json()['message']

    # TODO: get clientID by owner
    def client_ids_by_owner(self, owner):
        """
        Parameters
        ----------
        owner : str
            Username of the owner of the client application.

        Returns
        -------
            A list of client's ID owned by the user.

        """
        url = Client.base_URL + 'apps/by-owner'
        param = {'owner': owner}
        if self.token is None:
            self.request_token()
        header = self.header_builder()
        response = self._check_token(response=requests.get(url, headers=header, params=param),
                                     flag='GET', url=url, params=param)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            else:
                raise InternalError()
        clientObject = response.json()
        clientIDs = []
        for ct in clientObject:
            clientIDs.append(ct['clientID'])
        return clientIDs

    # TODO: get api usage count by client
    def usage_by_client(self, clientID, owner):
        """
        Parameters
        ----------
        clientID : str
            Client's ID of the application.

        owner : str
            Username of the owner of the client application.

        Returns
        -------
        int
            The number of requests made by the client.

        """
        url = Client.base_URL + "apps/" + clientID + "/usage"
        param = {'owner': owner}
        if self.token is None:
            self.request_token()
        header = self.header_builder()
        response = self._check_token(response=requests.get(url, headers=header, params=param),
                                     flag='GET', url=url, params=param)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 403:
                raise AuthorizationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            else:
                raise InternalError()
        return response.json()['api_usage']

    # TODO: add a camera to database
    def add_camera(self):
        pass

    def update_camera(self, cameraID, camera_type=None, is_active_image=None,
                      is_active_video=None, ip=None, snapshot_url=None, m3u8_url=None,
                      legacy_cameraID=None, source=None, latitude=None, longitude=None,
                      country=None, state=None, city=None, resolution_width=None,
                      resolution_height=None, utc_offset=None, timezone_id=None,
                      timezone_name=None, reference_logo=None, reference_url=None, port=None,
                      brand=None, model=None, image_path=None, video_path=None):

        """update_camera initialization method.

                Parameters
                ----------
                cameraID : str
                    Required cameraID for the update camera
                camera_type : str
                    Type of camera.
                    Allowed values: 'ip', 'non_ip', 'stream'/
                is_active_image : bool
                    If the camera is active and can get images.
                    This field can identify true/false case-insensitively and 0/1.
                is_active_video : bool
                    If the camera is active and can get video.
                    This field can identify true/false case-insensitively and 0/1.
                ip : str
                    (ip_camera) IP address of the camera.
                snapshot_url : str
                    (non_ip_camera) Url to retrieve snapshots from the camera.
                m3u8_url : str
                    (stream_camera) Url to retrieve stream from the camera.
                legacy_cameraID : num
                    Original ID of the camera in SQL database.
                source : str
                    Source of camera.
                latitude : str
                    Latitude of the camera location.
                longitude : str
                    Longitude of the camera location.
                country : str
                    Country which the camera locates at.
                state : str
                    State which the camera locates at.
                city : str
                    City which the camera locates at.
                resolution_width : num
                    Resolution width of the camera.
                resolution_height : num
                    Resolution height of the camera.
                utc_offset : num
                    Time difference between UTC and the camera location.
                timezone_id : str
                    Time zone ID of the camera location.
                timezone_name : str
                    Time zone name of the camera location.
                reference_logo : str
                    Reference logo of the camera.
                reference_url : str
                    Reference url of the camera.
                port : str
                    (ip_camera) Port to connect to camera.
                brand : str
                    (ip_camera) Brand of the camera.
                model : str
                    (ip_camera) Model of the camera.
                image_path : str
                    (ip_camera) Path to retrieve images from the camera.
                    if the camera is an ip camera and 'is_active_image' is true,
                    then it will always have a image_path.
                    However, image_path can exist even if 'is_active_image'
                    is false for this ip camera.
                video_path : str
                    (ip_camera) Path to retrieve video from the camera.
                    if the camera is an ip camera and 'is_active_video' is true,
                    then it will always have a video_path.
                    However, video_path can exist even if 'is_active_video'
                    is false for this ip camera.

                Raises
                ------
                    AuthenticationError
                        If the client secret of this client object does not match the clientID.
                    FormatError
                        List of invalid attributes.
                    ResourceConflictError
                        The legacy_cameraID already exist in the database.
                    InternalError
                        If there is an API internal error.
                    ResourceNotFoundError
                        If no client app exists with the clientID of this client object.

                Returns
                -------
                str
                    cameraID: the new camera ID for the created camera
        """

        local_params = dict(locals())

        if self.token is None:
            self.request_token()

        url = Client.base_URL + 'cameras/' + cameraID

        local_params['type'] = local_params.pop('camera_type')
        del local_params['self']

        if camera_type == 'ip':

            local_params['retrieval'] = {
                'ip': local_params.pop('ip'),
                'port': local_params.pop('port'),
                'brand': local_params.pop('brand'),
                'model': local_params.pop('model'),
                'image_path': local_params.pop('image_path'),
                'video_path': local_params.pop('video_path')
            }
        elif camera_type == 'non-ip':
            local_params['retrieval'] = {
                'snapshot_url': local_params.pop('snapshot_url')
            }
        elif camera_type == 'stream':
            local_params['retrieval'] = {
                'm3u8_url': local_params.pop('m3u8_url')
            }

        # Change the given dict into an object for API
        local_params['retrieval'] = json.dumps(local_params['retrieval'])

        response = self._check_token(requests.put(url, data=local_params, headers=self.header_builder()), flag='PUT',
                                     url=url, data=local_params)
        if response.status_code != 201:
            if response.status_code == 403:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            elif response.status_code == 409:
                raise ResourceConflictError(response.json()['message'])
            elif response.status_code == 401:
                self.request_token()
                response = requests.post(url, headers=self.header_builder(), data=local_params)
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            elif response.status_code == 500:
                raise InternalError()

        return response.json()['cameraID']

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
        elif response.status_code != 200:
            raise InternalError()
        camera_response_array = response.json()
        camera_processed = []
        for current_object in camera_response_array:
            camera_processed.append(Camera.process_json(**current_object))
        return camera_processed
