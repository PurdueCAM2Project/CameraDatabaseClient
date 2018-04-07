#from .camera import Camera, IPCamera, NonIPCamera, StreamCamera
#from .error import Error
import requests

class Client(object):
    """
    Represent a CAM2 client application.
    """
    # TODO: corresponding to the auth route
    @staticmethod
    def request_token(id, secret):
        url = 'https://cam2-api.herokuapp.com/auth/?'
        url += 'clientID='+id+'&clientSecret='+secret
        response = requests.get(url)
        return response.json()['token']

    # TODO: set authentication in header
    @staticmethod
    def header_builder(token):
        head = {'Authorization': 'Bearer ' + token}
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

if __name__ == '__main__':
    clinetID = "dd53cbd9c5306b1baa103335c4b3e91d8b73386ba29124ea2b1d47a619c8c066877843cd8a7745ce31021a8d1548cf2a"
    clientSecret = "f7ad9184949b914f2c73da4f6c82f6e93660c23c644e0ca4c9ac8268a141e02f258728aeefe864a6d03f709163cefe9c"
    Client = Client(clinetID,clientSecret)