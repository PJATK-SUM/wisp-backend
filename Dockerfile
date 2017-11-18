FROM resin/raspberrypi3-python:3
WORKDIR /usr/src/app
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . ./
ENV INITSYSTEM on
CMD ["python", "mirror.py"]
