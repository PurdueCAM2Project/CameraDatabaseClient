"""
Represents a CAM2 client application.
"""
import json
import requests
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError, \
    AuthorizationError, ResourceConflictError
from .camera import Camera


class Client(object):
    """Class representing a CAM2 client application.

    [More detailed description of what client object do.]


    Attributes
    ----------
    clientID : str
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
        those methods will rerun _request_token() to get a new token if token expires.
        But if the requests get status code of 401 for more than 2 times,
        we raise an Authentication error.

    """

    base_URL = 'https://cam2-api.herokuapp.com/'

    """str: Static variable to store the base URL.

    This is the URL of CAM2 Database API. User is able to send API calls directly to this URL.

    """

    _camera_fields = set(['reference_url', 'reference_logo', 'timezone_name', 'timezone_id',
                          'utc_offset', 'resolution_height', 'resolution_width', 'city',
                          'state', 'country', 'longitude', 'latitude', 'source',
                          'legacy_cameraID', 'm3u8_url', 'snapshot_url', 'is_active_video',
                          'is_active_image', 'camera_type', 'ip', 'port', 'brand', 'model',
                          'image_path', 'video_path', 'cameraID'])

    @staticmethod
    def _check_args(kwargs, legal_args):
        illegal_args = set(kwargs.keys()) - legal_args
        if illegal_args:
            raise FormatError('Keywords ' + str(list(illegal_args)) + ' are not defined.')

    def _check_token(self, response, flag, url, data=None, params=None):
        counter = 0
        while response.status_code == 401 and \
                response.json()['message'] == 'Token expired' and counter < 2:
            self._request_token()
            header = self.header_builder()
            if flag == 'GET':
                response = requests.get(url, headers=header, params=params)
            elif flag == 'POST':
                response = requests.post(url, headers=header, data=data)
            else:
                response = requests.put(url, headers=header, data=data)
            counter += 1
        return response

    def _request_token(self):

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

        url = self.base_URL + 'auth'
        param = {'clientID': self.clientID, 'clientSecret': self.clientSecret}
        response = requests.get(url, params=param)
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

    def __init__(self, clientID, clientSecret):

        """Client initialization method.

        Parameters
        ----------
        clientID : str
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
        if len(clientID) != 96:
            raise InvalidClientIdError
        if len(clientSecret) < 71:
            raise InvalidClientSecretError
        self.clientID = clientID
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
            self._request_token()
        header = self.header_builder()
        data = {'owner': owner, 'permissionLevel': permissionLevel}
        response = self._check_token(response=requests.post(url, headers=header, data=data),
                                     flag='POST', url=url, data=data)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()
        return response.json()['clientID'], response.json()['clientSecret']


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
            self._request_token()
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
            self._request_token()
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

    def reset_secret(self, clientID):
        """
        Parameters
        ----------

        clientID: str
            Client Id of the application.

        Returns
        --------
        str
            New clientSecret

        """
        url = Client.base_URL + 'apps/' + clientID + '/secret'
        if self.token is None:
            self._request_token()
        header = self.header_builder()
        response = self._check_token(response=requests.put(url, headers=header, data=None),
                                     flag='PUT', url=url, data=None)

        if response.status_code != 200:

            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])

            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])

            else:
                raise InternalError()

        return response.json()['clientSecret']

    def client_ids_by_owner(self, owner):
        """
        Parameters
        ----------
        owner : str
            Username of the owner of the client application.

        Returns
        -------
        list of str
            A list of client's ID owned by the user.

        """
        url = Client.base_URL + 'apps/by-owner'
        param = {'owner': owner}
        if self.token is None:
            self._request_token()
        header = self.header_builder()
        response = self._check_token(response=requests.get(url, headers=header, params=param),
                                     flag='GET', url=url, params=param)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            else:
                raise InternalError()
        clientObject = response.json()
        clientIDs = []
        for ct in clientObject:
            clientIDs.append(ct['clientID'])
        return clientIDs

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
            self._request_token()
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

    def write_camera(self, **kwargs):

        """
        add or update camera in the database.

        Parameters
        ----------
            camera_type : str
                Type of camera.
                Allowed values: 'ip', 'non_ip', 'stream'.
                | This parameter is required for adding camera.
            is_active_image : bool
                Whether the camera is active and can get images.
                This field can identify true/false case-insensitively and 0/1.
                | This parameter is required for adding camera.
            is_active_video : bool
                Whether the camera is active and can get video.
                This field can identify true/false case-insensitively and 0/1.
                | This parameter is required for adding camera.
            ip : str
                (IP camera only) IP address of the camera.
                | This parameter is required for adding an IP camera.
            snapshot_url : str
                (non-IP camera only) Url to retrieve snapshots from the camera.
                | This parameter is required for adding a non-IP camera.
            m3u8_url : str
                (Stream camera only) Url to retrieve stream from the camera.
                | This parameter is required for adding a stream camera.
            cameraID : str
                CameraID of the camera to be updated.
                | This parameter is required for updating camera.

        Note
        ----
            For adding camera to database, besides supplying the required parameters,
            you can also include any number of optional parameters defined below.
            You must not supply cameraID when you want to add a new camera to the database.
            A new cameraID will be generated and returned when the camera is successfully added.

            For updating existing camera, besides cameraID, you can also
            supply any number of parameters from required parameters to add a camera
            and optional parameters defined below.

            When adding or updating a camera you must supply the corresponding required parameters
            and may also include any number of the optional parameters defined below in 'Other Parameters. 

            When Adding a new camera: Do not include any cameraID when adding new cameras to the database.
            When the camera is added to the database a new cameraID will be assigned and returned to the user. 

            When updating an existing camera in the database you must include the corresponding cameraID
            and any fields you wish to update. If in any occasion you need to change an existing camera to
            a different type, you must include the corresponding retrieval method data.
            (i.e. To change an IP camera to non-ip you must include the snapshot_url and camera_type)

        Warning
        -------
            Including a cameraID in your write_camera request will update and overwrite the corresponding
            camera information in the database. Please ensure that the updated information is correct. 


        Other Parameters
        ----------------
            legacy_cameraID : int, optional
                Original ID of the camera in SQL database.
            source : str, optional
                Source of camera.
            latitude : int or float, optional
                Latitude of the camera location.
            longitude : int or float, optional
                Longitude of the camera location.
            country : str, optional
                Country which the camera locates at.
            state : str, optional
                State which the camera locates at.
            city : str, optional
                City which the camera locates at.
            resolution_width : int, optional
                Resolution width of the camera.
            resolution_height : int, optional
                Resolution height of the camera.
            utc_offset : int, optional
                Time difference between UTC and the camera location.
            timezone_id : str, optional
                Time zone ID of the camera location.
            timezone_name : str, optional
                Time zone name of the camera location.
            reference_logo : str, optional
                Reference logo of the camera.
            reference_url : str, optional
                Reference url of the camera.
            port : str or int, optional
                (ip_camera only) Port to connect to camera.
            brand : str, optional
                (ip_camera only) Brand of the camera.
            model : str, optional
                (ip_camera only) Model of the camera.
            image_path : str, optional
                (ip_camera only) Path to retrieve images from the camera.
            video_path : str, optional
                (ip_camera only) Path to retrieve video from the camera.

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
            The camera ID for the successfully added or updated camera.
        """

        self._check_args(kwargs=kwargs, legal_args=self._camera_fields)

        if self.token is None:
            self._request_token()

        operation = 'POST' if kwargs.get('cameraID') is None else 'PUT'

        if kwargs.get('camera_type') == 'ip':
            kwargs['retrieval'] = {
                'ip': kwargs.pop('ip', None),
                'port': kwargs.pop('port', None),
                'brand': kwargs.pop('brand', None),
                'model': kwargs.pop('model', None),
                'image_path': kwargs.pop('image_path', None),
                'video_path': kwargs.pop('video_path', None)
            }
            kwargs['retrieval'] = json.dumps(kwargs['retrieval'], sort_keys=True)

        elif kwargs.get('camera_type') == 'non_ip':
            kwargs['retrieval'] = {
                'snapshot_url': kwargs.pop('snapshot_url', None)
            }
            kwargs['retrieval'] = json.dumps(kwargs['retrieval'])
        elif kwargs.get('camera_type') == 'stream':
            kwargs['retrieval'] = {
                'm3u8_url': kwargs.pop('m3u8_url', None)
            }
            kwargs['retrieval'] = json.dumps(kwargs['retrieval'])
        kwargs['type'] = kwargs.pop('camera_type', None)

        if operation == 'POST':
            url = Client.base_URL + 'cameras/create'
            temp_response = requests.post(url, data=kwargs, headers=self.header_builder())
        else:
            url = Client.base_URL + 'cameras/' + kwargs.pop('cameraID')
            temp_response = requests.put(url, data=kwargs, headers=self.header_builder())

        response = self._check_token(temp_response, flag=operation, url=url, data=kwargs)

        if response.status_code != 201 and response.status_code != 200:
            if response.status_code == 403:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            elif response.status_code == 409:
                raise ResourceConflictError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            else:
                raise InternalError()

        return response.json()['cameraID']

    def camera_by_id(self, cameraID):
        """
        A method to get a camera object by using camera's ID

        Parameters
        ----------
        cameraID : str

        Returns
        -------
        :obj:`Camera`
            A camera object.

        """
        if self.token is None:
            self._request_token()
        url = Client.base_URL + "cameras/" + cameraID
        header = self.header_builder()
        response = self._check_token(response=requests.get(url, headers=header),
                                     flag='GET', url=url)

        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 404:
                raise ResourceNotFoundError(response.json()['message'])
            elif response.status_code == 403:
                raise AuthorizationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()
        return Camera.process_json(**response.json())

    def search_camera(self, latitude=None, longitude=None, radius=None, camera_type=None,
                      source=None, country=None, state=None, city=None, resolution_width=None,
                      resolution_height=None, is_active_image=None, is_active_video=None,
                      offset=None):

        """A method to search camera by attributes and location.

        Searching by location requires user to provide coordiantes for a desired center point
         and a radius in meters. The search will carry out in the area bounded by the circle.

        Parameters
        ----------
        latitude : float, optional
        longitude : float, optional
        radius : float, optional
        offset : int, optional
        camera_type : str, optional
        source : str, optional
        country : str, optional
        state : str, optional
        city : str, optional
        resolution_width : int, optional
        resolution_height : int, optional
        is_active_image : bool, optional
        is_active_video : bool, optional

        Returns
        -------
        :obj:`list` of :obj:`Camera`
            List of cameras that satisfy the search criteria.

        Raises
        ------
        FormatError
            If type of argument value is not expected for the given field.

            Or radius cannot is less than 0.

            Or incorrect latitude range. (it should be between +90 and -90)

            Or incorrect longitude range. (it should be between +180 and -180)

        AuthenticationError
            If the client secret of this client object does not match the clientID.
        ResourceNotFoundError
            If the client id of this client object does not match any client
            in the database.
        InternalError
            If there is an API internal error.

        """
        if self.token is None:
            self._request_token()
        local_params = dict(locals())
        local_params.pop('self', None)
        local_params['type'] = local_params.pop('camera_type', None)

        # filter out those parameters with value None, change true/false
        search_params = {k: v for k, v in local_params.items() if v is not None}

        url = Client.base_URL + 'cameras/search'
        header = self.header_builder()
        response = self._check_token(
            response=requests.get(url, headers=header, params=search_params),
            flag='GET', url=url, params=search_params)

        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()

        camera_response_array = response.json()
        camera_processed = []
        for current_object in camera_response_array:
            camera_processed.append(Camera.process_json(**current_object))

        return camera_processed

    def check_cam_exist(self, camera_type, **kwargs):
        """
        A method to get one or more camera object that has the given retrieval method
        in the database.

        Parameters
        ----------
        camera_type : str
            Type of the camera. Type can only be 'ip', 'non_ip', or 'stream'.
        ip : str, optional
            [for IP camera] Ip address of the camera. Although marked as optional,
            this field is required when the camera type is 'ip'.
        port : Int, optional
            [for IP camera] Port of the camera. If no port provided, it will be set to default 80.
        image_path : str, optional
            [for IP camera] Path to retrieve images from the camera.
        video_path : str, optinal
            [for IP camera] Path to retrievae vidoe from the camera.
        snapshot_url : str, optional
            [for non_IP camera] Url to retrieval image frames from the camera.
            Although marked as optional, this field is required when the camera type is 'non_ip'.
        m3u8_url : str, optional
            [for stream camera] Url to retrieval video stream from the camera.
            Although marked as optional, this field is required when the camera type is 'stream'.

        Returns
        -------
        :obj:`list` of :obj:`Camera`
            List of camera objects that has the given retrieval method. If there ar eno cameras
            matches the provided retrieval information, an empty list will be returned.

        Raises
        ------
        FormatError
            If camera type is not valid.

            or camera type is not provided.

            or ip is not provided when the camera type is 'ip'.

            or snapshot_url is not provided when the camera type is 'non_ip'.

            or m3u8_url is not provided whe nthe camera ytpe is 'stream'.

        AuthenticationError
            If the client secret of this client object does not match the clientID.
        ResourceNotFoundError
            If the client id of this client object does not match any client
            in the database.
        InternalError
            If there is an API internal error.
        """
        url = Client.base_URL + "cameras/exist"
        kwargs['type'] = camera_type

        # validate parameter names here.

        if self.token is None:
            self._request_token()
        header = self.header_builder()
        response = self._check_token(response=requests.get(url, headers=header, params=kwargs),
                                     flag='GET', url=url, params=kwargs)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()
        camera_response_array = response.json()
        camera_processed = []
        for current_object in camera_response_array:
            camera_processed.append(Camera.process_json(**current_object))
        return camera_processed

    def get_change_log(self, start=None, end=None, offset=None):
        """
        Parameters
        ----------
        start : str, optional
            Start time of the log user desires to query
        end : str, optional
            End time of the log user desires to query
        offset : str, optional
            How many logs to skip

        Returns
        -------
        list of dict of {str : str}
            A list of objects containing cameraID and creation time of the log.

        Raises
        ------
        AuthenticationError
            If the client secret of this client object does not match the clientID.
        InternalError
            If there is an API internal error.
        FormatError
            If type of argument value is not expected for the given field.

        """
        url = Client.base_URL + 'apps/db-change'
        if self.token is None:
            self._request_token()
        header = self.header_builder()
        param = {'start': start,
                 'end': end,
                 'offset': offset}
        response = self._check_token(response=requests.get(url, headers=header, params=param),
                                     flag='GET', url=url, params=param)
        if response.status_code != 200:
            if response.status_code == 401:
                raise AuthenticationError(response.json()['message'])
            elif response.status_code == 422:
                raise FormatError(response.json()['message'])
            else:
                raise InternalError()

        return response.json()
