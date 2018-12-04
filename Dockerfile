FROM python:3.6
WORKDIR /usr/src/tests
COPY . .
RUN pip install -r requirements.txt
RUN python3 -m unittest discover

FROM python:2.7
WORKDIR /usr/src/tests
COPY . .
RUN pip install -r requirements.txt
RUN python -m unittest discover

FROM python:3.6-alpine
WORKDIR /usr/src/pylint
COPY . .
RUN pip install -r requirements.txt
CMD  [ "pylint", "./CAM2CameraDatabaseAPIClient/client.py" ]
