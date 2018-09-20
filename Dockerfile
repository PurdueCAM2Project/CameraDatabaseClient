FROM python:3
WORKDIR /usr/src/tests
COPY . .
RUN pip install -r requirements.txt
RUN python3 -m unittest discover
RUN python -m unittest discover

FROM python:3.4-alpine
WORKDIR /usr/src/pylint
COPY . .
RUN pip install -r requirements.txt
COPY . .
CMD  [ "pylint", "./CAM2CameraDatabaseAPIClient/client.py" ]
