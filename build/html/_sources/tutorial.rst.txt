====================================
Quickstart
====================================

We will present here some basic usage examples, please see the full documentation for 

First, make sure that CAM2 Camera Database API Client is successfully installed, and a pair of valid client ID and secret to access the API has been issued to you. 

You can refer to :ref:`install-ref` and :ref:`Obtaining API Access <API-access-ref>`.


Create Client Instance
------------------------

Begin be import CAM2 Camera Database API Client package.

>>> from CAM2CameraDatabaseAPIClient.client import Client

Then, create a Client object using client ID and secret to access the Camera Database API. Creating a valid Client object is the prerequsite of calling any functions for getting camera data or managing user clients. 

>>> clientID = <96 Character Client ID>
>>> clientSecret = <71 Character Client Secret>
>>> db = Client(clientID, clientSecret)

Query Camera by City
---------------------------------------------

We can query the CAM2 API by using the :meth:`~CAM2CameraDatabaseAPIClient.client.Client.search_camera` method. Please check the detailed method documentation for list of filters that can be applied on results returned.

>>> cameras = db.search_camera(city="West Lafayette", offset=0)

This will return a list of 100 camera :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` objects that match the search query constraints. To get one camera object from the query we can index into the list as following:

>>> cameras[0]
{u'utc_offset': -18000, u'resolution_width': 640, u'image_path': u'/axis-cgi/jpg/image.cgi', u'ip': u'128.10.29.20', u'brand': u'Axis', u'reference_logo': None, u'cameraID': u'5b0cfa7345bb0c0004277e29', u'latitude': 40.4278, u'longitude': -86.9169, u'frame_rate': None, u'port': u'80', u'city': u'West Lafayette', u'timezone_id': u'Eastern Daylight Time', u'legacy_cameraID': 14, u'video_path': u'/axis-cgi/mjpg/video.cgi', u'is_active_video': False, u'is_active_image': False, u'source': u'opentopia', u'state': u'IN', 'camera_type': u'ip', u'reference_url': u'128.10.29.20/axis-cgi/mjpg/video.cgi', u'resolution_height': 480, u'timezone_name': u'Eastern Standard Time', u'model': None, u'country': u'USA'}

The API will only return a limit of 100 cameras at a time. To access the next 100 cameras on the API we can change the offset parameter to 100.


Access Camera Attributes
---------------------------

To make accessing camera attributes simple, the :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` object behaves like a dictionary class. 

For example:

>>> cameras[0]['resolution_height']
480	
>>> cameras[0]['resolution_width']
640
>>> cameras[0]['image_path']
u'/axis-cgi/jpg/image.cgi'

A full list of camera object attributes and their descriptions can be found in :class:`~CAM2CameraDatabaseAPIClient.camera.Camera` class.

.. _image-archiver-ref:

Use Client with CAM2 Image Archiver 
------------------------------------------------------------

The CAM2 Image Archiver allows users to download network camera image data from camera objects and save them to the local machine. 

