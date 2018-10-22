====================================
Quickstart
====================================

We will present here some basic usage examples, please see the full documentation for 

First, make sure that CAM2 Camera Database API Client is successfully installed, and a pair of valid client ID and secret to access the API has been issued to you. 

You can refer to :ref:`install-ref` and :ref:`Obtaining API Access <API-access-ref>`.


Create Client Instance
------------------------

Begin be import CAM2 Camera Database API Client package.

>>> import CAM2CameraDatabaseAPIClient as cam2

Then, create a Client object using client ID and secret to access the Camera Database API. Creating a valid Client object is the prerequsite of calling any functions for getting camera data or managing user clients. 

>>> clientID = <96 Character Client ID>
>>> clientSecret = <71 Character Client Secret>
>>> db = cam2.Client(clientID, clientSecret)

.. _camera-by-city-ref:

Query Camera by City
---------------------------------------------

We can query the CAM2 API by using the :meth:`~CAM2CameraDatabaseAPIClient.client.Client.search_camera` method. Please check the detailed method documentation for list of filters that can be applied on results returned.

>>> cameras = db.search_camera(city="West Lafayette", offset=0)

This will return a list of 100 camera :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` objects that match the search query constraints. To access the next 100 cameras on the API we can change the offset parameter to 100.

To get one camera object from the query we can index into the list as following:

>>> cameras[0]
{u'utc_offset': -18000, u'resolution_width': 640, u'image_path': u'/axis-cgi/jpg/image.cgi', u'ip': u'128.10.29.20', u'brand': u'Axis', u'reference_logo': None, u'cameraID': u'5b0cfa7345bb0c0004277e29', u'latitude': 40.4278, u'longitude': -86.9169, u'frame_rate': None, u'port': u'80', u'city': u'West Lafayette', u'timezone_id': u'Eastern Daylight Time', u'legacy_cameraID': 14, u'video_path': u'/axis-cgi/mjpg/video.cgi', u'is_active_video': False, u'is_active_image': False, u'source': u'opentopia', u'state': u'IN', 'camera_type': u'ip', u'reference_url': u'128.10.29.20/axis-cgi/mjpg/video.cgi', u'resolution_height': 480, u'timezone_name': u'Eastern Standard Time', u'model': None, u'country': u'USA'}

Query Camera by Coordinates
---------------------------------------------

If you have seen the full documentation of the :meth:`~CAM2CameraDatabaseAPIClient.client.Client.search_camera` method, you should have realized that a camera has address at most precise to city. When this scope is still too large for a specific search query, need arises to have a more refined area as search constraint. 

A specific circle area on Earth can be defined by a center and radius. 

We can query the CAM2 API for cameras in a specific circle area by using the :meth:`~CAM2CameraDatabaseAPIClient.client.Client.search_camera` method with a pair of coordinates a center of the circle and radius in km as circle radius. 

>>> cameras = db.search_camera(latitude=40.4278, longitude=-86.9169, radius=50, offset=0)

This will return a list of 100 camera :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` objects that are in the circle area defined by the coordinate center and radius of 50km. To access the next 100 cameras on the API we can change the offset parameter to 100.

To get one camera object from the query we can index into the list as described in :ref:`camera-by-city-ref`.

Access Camera Attributes
---------------------------

To make accessing camera attributes simple, the :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` object behaves like a dictionary class.

For example, user can access the first camera in a list of cameras by:

>>> cameras[0]['resolution_height']
480	
>>> cameras[0]['resolution_width']
640

Keep in mind that there are 3 types of camera, namely :class:`~CAM2CameraDatabaseAPIClient.camera.IPCamera`, :class:`~CAM2CameraDatabaseAPIClient.camera.NonIPCamera`, and :class:`~CAM2CameraDatabaseAPIClient.camera.StreamCamera`. Most of the attributes are common to all three type of camera, but the attributes related to retrieval method of the camera will be different for different types of camera.

For example, user can check the image_path of an IP camera and is recommanded to check the camera type before checking retrieval method related attributes.

>>> camera['camera_type']
u'ip'
>>> camera['image_path']
u'/axis-cgi/jpg/image.cgi'

A full list of camera object attributes and their descriptions can be found in :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` class.

.. _image-archiver-ref:

Use Client with CAM2 Image Archiver 
------------------------------------------------------------

The CAM2 Image Archiver allows users to download network camera image data from camera objects and save them to the local machine. 
See more at:

https://github.com/PurdueCAM2Project/CAM2ImageArchiver