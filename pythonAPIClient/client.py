from .camera import Camera, IPCamera, NonIPCamera, StreamCamera
from .error import Error
import requests

class Client(object):
    """
    Represent a CAM2 client application.
    """
    # TODO: corresponding to the auth route
    @staticmethod
    def request_token(id, secret):
        return 'dummy'

    # TODO: set authentication in header
    @staticmethod
    def header_builder(token):
        return 'dummy'

    def __init__(self, id, secret, token=None):
        self.id = id
        self.secret = secret
        if token is None: 
            self.token = Client.request_token(id, secret)
        self.token = token

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

    """
    Function for admin
    """

    # TODO: add a camera to database
    def add_camera(self, Camera):
        pass

    # TODO: update a camera in database
    # replace others with desired field names
    def update_camera(self, camID, others):
        pass

    """
    Function for user
    """

    # TODO: get a camera
    def camera_by_id(self, cameraID):
        pass

    # TODO: search a camera
    # replace others with desired field names
    def search_camera(self, others):
        pass
