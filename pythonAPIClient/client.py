from .camera import Camera, IPCamera, NonIPCamera, StreamCamera
from .error import Error
import requests

class Client(object):

    """
    Represent a CAM2 client application.
    """
    # TODO: corresponding to the auth route
    def request_token(self):
        url = 'https://cam2-api.herokuapp.com/auth/?'
        url += 'clientID='+self.id+'&clientSecret='+self.secret
        response = requests.get(url)
        if(response.status_code == 200):
            self.token = response.json()['token']
            return "OK"
        else:
            return str(response.status_code) + "-" + response.json()['message']

    # TODO: set authentication in header
    def header_builder(self):
        head = {'Authorization': 'Bearer ' + str(self.token)}
        return head

    def __init__(self, id, secret):
        self.id = id
        self.secret = secret
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