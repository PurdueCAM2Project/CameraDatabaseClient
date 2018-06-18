"""
Represents a CAM2 client application.
"""
import requests
from .error import AuthenticationError, InternalError, InvalidClientIdError, \
    InvalidClientSecretError, ResourceNotFoundError, FormatError
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

    """

    base_URL = 'https://cam2-api.herokuapp.com/'
    """str: Static variable to store the base URL.

    This is the URL of CAM2 Database API. User is able to send API calls directly to this URL.

    """

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
            Client secret should have a length of at least 71 characters

        """

        if len(clientId) != 96:
            raise InvalidClientIdError
        if len(clientSecret) != 71:
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

        Raises
        ------

        Returns
        -------
        str
            Client id of the newly registered client application.
        str
            Client secret of the newly registered client application.
        """
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
        elif response.status_code != 200:
            raise InternalError()
        camera_response_array = response.json()
        camera_processed = []
        for current_object in camera_response_array:
            camera_processed.append(Camera.process_json(**current_object))
        return camera_processed
