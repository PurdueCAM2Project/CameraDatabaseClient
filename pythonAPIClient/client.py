"""
Represents a CAM2 client application.
"""
import requests
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError, AuthorizationError
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
    def add_camera(self, camera):
        pass

    # TODO: update a camera in database
    # replace others with desired field names
    def update_camera(self, camID, others):
        pass

    # TODO: get a camera
    def camera_by_id(self, cameraID):
        pass

    def search_camera(self, latitude=None, longitude=None, radius=None, camera_type=None,
                      source=None, country=None, state=None, city=None, resolution_width=None,
                      resolution_heigth=None, is_active_image=None, is_active_video=None,
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
        InternalError
            If there is an API internal error.

        """
        if self.token is None:
            self.request_token()
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
            elif response.status_code != 200:
                raise InternalError()

        camera_response_array = response.json()
        camera_processed = []
        for current_object in camera_response_array:
            camera_processed.append(Camera.process_json(**current_object))

        return camera_processed
