====================================
Tutorial
====================================


A simple example
---------------------------------

Importing the CAM2 Camera API Client Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from CAM2CameraDatabaseAPIClient.client import Client

Creating Client Instance
^^^^^^^^^^^^^^^^^^^^^^^^

You can request a Client ID and Client Secret from your user account on the `CAM2 Website <https://www.cam2project.net/>`_.

>>> clientID = <96 Character Client ID>
>>> clientSecret = <71 Character Client Secret>
>>> db = Client(clientID, clientSecret)

Querying the CAM2 Camera API by City
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can query the CAM2 API by using the :meth:`~CAM2CameraDatabaseAPIClient.client.Client.search_camera` method.

>>> cameras = db.search_camera(city="West Lafayette", offset=0)

This will return a list of 100 camera :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` objects that match the search query. To extract one camera object from the query we can do:

>>> cameras[0]
{u'utc_offset': -18000, u'resolution_width': 640, u'image_path': u'/axis-cgi/jpg/image.cgi', u'ip': u'128.10.29.20', u'brand': u'Axis', u'reference_logo': None, u'cameraID': u'5b0cfa7345bb0c0004277e29', u'latitude': 40.4278, u'longitude': -86.9169, u'frame_rate': None, u'port': u'80', u'city': u'West Lafayette', u'timezone_id': u'Eastern Daylight Time', u'legacy_cameraID': 14, u'video_path': u'/axis-cgi/mjpg/video.cgi', u'is_active_video': False, u'is_active_image': False, u'source': u'opentopia', u'state': u'IN', 'camera_type': u'ip', u'reference_url': u'128.10.29.20/axis-cgi/mjpg/video.cgi', u'resolution_height': 480, u'timezone_name': u'Eastern Standard Time', u'model': None, u'country': u'USA'}

The API will only return a limit of 100 cameras at a time. To access the next 100 cameras on the API we can change the offset parameter to 100.


Accessing Camera Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make accessing camera attributes simple, the :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` object behaves like a dictionary class. For example:

>>> cameras[0]['resolution_height']
480	
>>> cameras[0]['resolution_width']
640
>>> cameras[0]['image_path']
u'/axis-cgi/jpg/image.cgi'

A full list of camera object attributes and their descriptions can be found in :class:`~CAM2CameraDatabaseAPIClient.camera.Camera`


Using the Client In Conjunction With the CAM2 Image Archiver 
------------------------------------------------------------

The CAM2 Image Archiver allows users to download network camera image data from camera objects and save them to the local machine. 

