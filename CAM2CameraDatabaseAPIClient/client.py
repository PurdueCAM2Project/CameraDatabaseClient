"""
Represents a CAM2 client application.
"""
import json
import requests
from .config import SECRET_LENGTH, CLIENTID_LENGTH
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError, \
    AuthorizationError, ResourceConflictError
from .camera import Camera


class Client(object):
    """Class representing a CAM2 client application.


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

    """

    base_URL = 'https://cam2-api.herokuapp.com/'

    """str: Static variable to store the base URL.

    This is the URL of CAM2 Database API. User is able to send API calls directly to this URL.

    """

    _camera_fields = set(['reference_url', 'reference_logo', 'timezone_name', 'timezone_id',
                          'utc_offset', 'resolution_height', 'resolution_width', 'city',
                          'state', 'country', 'longitude', 'latitude', 'frame_rate', 'source',
                          'legacy_cameraID', 'm3u8_url', 'snapshot_url', 'is_active_video',
                          'is_active_image', 'camera_type', 'ip', 'port', 'brand', 'model',
                          'image_path', 'video_path', 'cameraID'])

    """
    set: Static private variable to store all legal keywords for adding or updating a camera.
    """

    _search_fields = set(['resolution_height', 'resolution_width', 'city', 'is_active_video',
                          'state', 'country', 'longitude', 'latitude', 'source', 'camera_type',
                          'is_active_image', 'radius', 'offset'])

    """
    set: Static private variable to store all legal keywords for searching cameras.
    """

    _retrieval_fields = set(['ip', 'port', 'image_path', 'video_path', 'snapshot_url', 'm3u8_url'])

    """
    set: Static private variable to store all legal keywords in kwargs in check camera
         existence function.
    """

    @staticmethod
    def _check_args(kwargs, legal_args):

        illegal_args = set(kwargs.keys()) - legal_args
        if illegal_args:
            raise FormatError('Keywords ' + str(list(illegal_args)) + ' are not defined.')

    def _check_token(self, response, flag, url, data=None, params=None):
        counter = 0
        while response.status_code == 401 and \
                response.json()['message'] == 'Token expired.' and counter < 2:
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
        if len(clientID) != CLIENTID_LENGTH:
            raise InvalidClientIdError
        if len(clientSecret) < SECRET_LENGTH:
            raise InvalidClientSecretError
        self.clientID = clientID
        self.clientSecret = clientSecret
        self.token = None

    # Functions for webUI

    def register(self, owner, permissionLevel='user'):
        """
        Create a client to use CamraDatabaseAPI

        Warning
        ---------
        You can only use this function if your client has webUI permission.

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


        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            # WebUI team developer created an client object
            webUI_client.register(ownerName, permissionLevel)

            User with webUI permission will use this method to
            register a client with owner's name and permission level.
            Scenario:
                Developer in webUI team wants to register a client for normal user whose name is Bob
                webUI_client = Client('1', '1')
                webUI_client.register('Bob', 'user')

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
        Update owner's username for the given clientID.

        Warning
        ---------
        You can only use this function if your client has webUI permission.

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

        Example
        -------
            webUI_client = Client(clientID, clientSecret)
            webUI_client.update_owner(userClientID, ownerName)

            User with webUI permission will use this method to
            update owner of a client given specific clientID.
            Scenario:
                Developer in webUI team wants to change
                the owner of clientID 2123 from 'Bob' to 'Ken'
                webUI_client.update_owner('2123', 'Ken')

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
        Update owner's permissionLevel for the given clientID.

        Warning
        ---------
        You can only use this function if your client has webUI permission.

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

        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            webUI_client.update_permission(userClientID, 'webUI')

            User with webUI permission will use this method
            to update permission of a client given specific clientID.
            Scenario:
                Developer in webUI team wants to change
                the permission of clientID 2123 from 'user' to 'webUI'
                webUI_client.update_permission('2123', 'webUI')

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
        A method to reset client secret.

        Warning
        ---------
        You can only use this function if your client has webUI permission.

        Parameters
        ----------

        clientID: str
            Client Id of the application.

        Returns
        --------
        str
            New clientSecret

        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            webUI_client.reset_secret(userClientID)

            User with webUI permission will use this method
            to reset secret key of a client given specific clientID.
            Scenario:
                Developer in webUI team wants to change the secret key of clientID 2123
                webUI_client.reset_secret('2123'')
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
        A method to get all client ids for a specific owner.

        Warning
        ---------
        You can only use this function if your client has webUI permission.

        Parameters
        ----------
        owner : str
            Username of the owner of the client application.

        Returns
        -------
        list of str
            A list of client's ID owned by the user.

        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            webUI_client.client_ids_by_owner(ownerName)

            User with webUI permission will use this method
            to get a list of clientIDs that belongs to a user.
            Scenario:
                Developer in webUI team wants to get
                all clientIDs that belongs to user named 'Bob'
                webUI_client.client_ids_by_owner('Bob')

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
        A method to get number of API requests made by a given clientID.

        Warning
        ---------
        You can only use this function if your client has webUI permission.

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

        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            webUI_client.usage_by_client(userClientID, ownerName)

            User with webUI permission will use this method
            to get number of API requests made by clientID 2123
            Scenario:
                Developer in webUI team wants to get number of API requests
                made by clientID 2123 whose owner is 'Bob'
                webUI_client.usage_by_client('2123', 'Bob')

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
        Add or update camera in the database.

        Warning
        ---------
        You can only use this function if your client has admin permission.

        Examples
        --------
            * Adding a camera of type 'IP' into the database:

            **Each type of camera has its unique fields.
            Please check the** :ref:`Parameters <write-param-ref>` **of this function or**
            :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` **for eligible fields
            of the type of camera you are working on.**

            Create a keyword arguments dictionary which contains all the parameters
            needed to create the camera (fields with value ``None`` can be omitted):

            >>> kwargs = {'camera_type': 'ip', 'is_active_image': True,
                          'is_active_video': False, 'ip': '127.0.0.1', 'snapshot_url': None,
                          'm3u8_url': None, 'cameraID': None, ...}

            Pass the keyword arguments dictionary to the write_camera function:

            >>> client.write_camera(**kwargs)

            Or, you can directly call the method with all parameters:

            >>> client.write_camera(camera_type='ip', is_active_image=True,
                          is_active_video=False, ip='127.0.0.1', snapshot_url=None, ...)

            * Updating a camera of type 'IP' in the database:

            One subtle difference of updating an existing camera from adding a new camera
            is that only ``cameraID``, ``camera_type``, and fields to be updated need to
            be included as a parameter with non-None value to update the camera.

            Create a keyword arguments dictionary which contains all the parameters
            needed to update the camera; in this example, user will update the ip
            address of this ip camera:

            >>> kwargs = {'ip': '127.0.0.2', 'camera_type': 'ip',
                          'cameraID': '5ae0ecbd336359291be74c12'}

            Pass the keyword arguments dictionary to the write_camera function:

            >>> client.write_camera(**kwargs)

            Or, you can directly call the method with all parameters:

            >>> client.write_camera(camera_type='ip', ip='127.0.0.2',
                          cameraID='5ae0ecbd336359291be74c12')

            * Adding or updating a camera of type 'non_ip':

            Following the above example of adding and updating IP camera, the only difference
            lies in the required fields.

            Example of adding a non-ip camera into database:

            >>> kwargs = {'camera_type': 'non_ip', 'is_active_image': True,
                          'is_active_video': False, 'ip': None, 'snapshot_url': test_url,
                          'm3u8_url': None, 'cameraID': None, ...}
            >>> client.write_camera(**kwargs)

            Example of updating the snapshot url and country of a camera of type 'non_ip':

            >>> client.write_camera(camera_type='non_ip', snapshot_url='updated_test_url',
                          country='JP', cameraID': '5ae0ecbd336359291be74c12'}

            * Adding or updating a camera of type 'stream':

            Following the above example of adding and updating IP camera, the only difference
            lies in the required fields.

            Example of adding a stream camera into database:

            >>> client.write_camera(camera_type='stream', is_active_image=True,
                          is_active_video=False, m3u8_url='test_url', cameraID=None, ...)

            Example of updating the m3u8_url of a camera of type 'stream':

            >>> write_camera(camera_type='stream', m3u8_url='test_url',
                          cameraID='5ae0ecbd336359291be74c12')

        .. _write-param-ref:

        Parameters
        ----------
            camera_type : str
                Type of camera.
                Allowed values: 'ip', 'non_ip', 'stream'.
                |  This parameter is required for adding camera.
            is_active_image : bool
                Whether the camera is active and can get images.
                This field can identify true/false case-insensitively and 0/1.
                |  This parameter is required for adding camera.
            is_active_video : bool
                Whether the camera is active and can get video.
                This field can identify true/false case-insensitively and 0/1.
                |  This parameter is required for adding camera.
            ip : str
                (IP camera only) IP address of the camera.
                |  This parameter is required for adding an IP camera.
            snapshot_url : str
                (non-IP camera only) Url to retrieve snapshots from the camera.
                |  This parameter is required for adding a non-IP camera.
            m3u8_url : str
                (Stream camera only) Url to retrieve stream from the camera.
                |  This parameter is required for adding a stream camera.
            cameraID : str
                CameraID of the camera to be updated.
                |  This parameter is required for updating camera.

        Warning
        -------
            Including a cameraID in your write_camera request will update and overwrite the
            corresponding camera information in the database.
            Please ensure that the updated information is correct.

        Other Parameters
        ----------------
            legacy_cameraID : int, optional
                Original ID of the camera in SQL database.
            frame_rate : int, optional
                Frame-rate of the camera.
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
                Informartion of invalid parameter or unexpected paramters.
            ResourceConflictError
                The legacy_cameraID already exist in the database.
            InternalError
                If there is an API internal error.
            ResourceNotFoundError
                If no camera exists with the cameraID specified in the parameter.

                Or If the client id of this client object does not match any client
                in the database.

        Returns
        -------
        str
            The camera ID for the successfully added or updated camera.

        Note
        ----
        When adding or updating a camera you must supply the corresponding required parameters
        and may also include any number of the optional parameters defined below in
        'Other Parameters'.

        When Adding a new camera:
        Do not include any cameraID when adding new cameras to the database.
        When the camera is added to the database, a new cameraID will be assigned and returned
        to the user.

        When updating an existing camera in the database you must include the corresponding
        cameraID and any fields you wish to update.
        If in any occasion you need to change an existing camera to a different type,
        you must include the corresponding retrieval method data.
        (i.e. To change an IP camera to non-ip camera, you must include values of snapshot_url
        and camera_type) Updating field in retrieval method requires you to also specify the
        type of camera. (i.e. To change the image_path of an IP camera, you should specify the
        camera_type and image_path)

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
            Id of the camera in the database.

        Returns
        -------
        :obj:`Camera`
            A camera object.

        Example
        -------

            client.camera_by_id('5ae0ecbc336359291be74c0b')

        Example
        -------

            user_client = Client(clientID, clientSecret)
            user_client.camera_by_id(cameraID)

            Programmer with 'user' permission will use this method
            to get a camera object with specified cameraID
            Scenario:
                Normal user wants to get a camera object which has a id of '12938263'
                user_client.camera_by_id('12938263')


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

    def camera_by_legacy_id(self, legacy_cameraID):
        """
        A method to get a camera object by using camera's legacy ID

        Parameters
        ----------
        legacy_cameraID : str
            legacy_cameraID of the camera in the database.

        Returns
        -------
        :obj:`Camera`
            A camera object.

        """
        if self.token is None:
            self._request_token()
        url = Client.base_URL + "cameras/legacy/" + legacy_cameraID
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

    def camera_by_list_id(self, cameraID_list=None, legacy_cameraID_list=None):
        """
        A method to get a list of camera object by using a list of camera's legacy ID or ID.

        Parameters
        ----------
        legacy_cameraID_list : List
            legacy_cameraIDs of the cameras in the database.

        cameraID_list : List
            cameraIDs of the cameras in the database.

        Returns
        -------
        :obj:`list` of :obj:`Camera`
            List of cameras that satisfy the search criteria.

        """
        camera_processed = []
        for ID in cameraID_list:
            camera_processed.append(self.camera_by_id(ID))
        for legacy_ID in legacy_cameraID_list:
            camera_processed.append(self.camera_by_legacy_id(legacy_ID))

        return camera_processed

    def search_camera(self, **kwargs):

        """A method to search camera by attributes and location.
        Searching by location requires user to provide coordiantes for a desired center point
        and a radius in meters. The search will carry out in the area bounded by the circle.
        Each time, this function can return a maximum of 100 cameras. Getting more cameras can
        be achieved by calling this function multiple times with offest parameter.

        Examples
        --------
            - Searching a camera of type 'IP' into the database with city as 'West Lafayette'
            Create a keyword arguments dictionary which contains all the parameters
            needed to search the camera:
                kwargs = {'camera_type': 'ip', 'city': 'West Lafayette'}
            Pass the keyword arguments dictionary to the search_camera function:
                a_client = Client('id', 'pass')
                a_client.search_camera(**kwargs)

            - Another way to search for cameras with the same parameters can be done by
            the following code:
                 a_client = Client('id', 'pass')
                 a_client.search_camera(camera_type='ip', city='West Lafayette')
        Parameters
        ----------

        latitude : float, optional
            Latitude of the center of the circle area to be searched.
            Latitude ranges between +90 and -90.

            Please specify longitude and radius if this parameter value is provided.
        longitude : float, optional
            Longitude of the center of the circle area to be searched.
            Longitude ranges between +180 and -180.

            Please specify latitude and radius if this parameter value is provided.
        radius : float, optional
            Radius in km of the circle area to be searched. Radius should be positive

            Please specify latitude and longitude if this parameter value is provided.
        offset : int, optional
            Number of cameras skipped. Since each time this function can return max 100 cameras,
            calling this function the second time adding `offset=100` will get the second 100
            cameras beyond the first list of 100 cameras.
        camera_type : str, optional
            Type of camera.
            Allowed values: 'ip', 'non_ip', 'stream'.
        source : str, optional
            Source of the camera.
        country : str, optional
            Country which the camera locates at.
        state : str, optional
            State which the camera locates at.
        city : str, optional
            City which the camera locates at.
        resolution_width : int, optional
            Resolution width of the camera. It has to be positive.
        resolution_height : int, optional
            Resolution height of the camera. It has to be positive.
        is_active_image : bool, optional
            If the camera is active and can get images.
            This field can identify true/false case-insensitively and 0/1.
        is_active_video : bool, optional
            If the camera is active and can get video.
            This field can identify true/false case-insensitively and 0/1.

        Returns
        -------
        :obj:`list` of :obj:`Camera`
            List of cameras that satisfy the search criteria.

        Raises
        ------
        FormatError

            If type of argument value is not expected for the given field.

            Or there are unexpected keywords in kwargs.

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

        self._check_args(kwargs, self._search_fields)

        kwargs['type'] = kwargs.pop('camera_type', None)

        # filter out those parameters with value None, change true/false
        search_params = {k: v for k, v in kwargs.items() if v is not None}

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
            List of camera objects that has the given retrieval method. If there are no cameras
            matches the provided retrieval information, an empty list will be returned.

        Raises
        ------
        FormatError
            If camera type is not valid.

            Or camera type is not provided.

            Or ip is not provided when the camera type is 'ip'.

            Or snapshot_url is not provided when the camera type is 'non_ip'.

            Or m3u8_url is not provided when the camera ytpe is 'stream'.

            Or there are unexpected keywords in kwargs.

        AuthenticationError
            If the client secret of this client object does not match the clientID.
        ResourceNotFoundError
            If the client id of this client object does not match any client
            in the database.
        InternalError
            If there is an API internal error.
        """

        self._check_args(kwargs, self._retrieval_fields)

        url = Client.base_URL + "cameras/exist"
        kwargs['type'] = camera_type

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
        A method to get change_log for a specific time period

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
        :obj:`list` of dict
            A list of objects containing cameraID and creation time of the log.

        Raises
        ------
        AuthenticationError
            If the client secret of this client object does not match the clientID.
        InternalError
            If there is an API internal error.
        FormatError
            If type of argument value is not expected for the given field.

        Example
        -------

            webUI_client = Client(clientID, clientSecret)
            webUI_client.get_change_log(start, end, offset)

            Programmer with 'webUI' permission will use this method
            to get change_log for a specific time period
            Scenario:
                Developer in webUI team wants to get 10 activities between the below time frame
                webUI_client.get_change_log('2018-08-27T15:53:00', '2018-08-27T16:53:00', 10)


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
