FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone &&  \
    apt-get update -y &&  \
    apt-get install -y python3-pip python3.11 build-essential libgl1-mesa-glx ffmpeg libsm6 libxext6 && \
    apt-get install -y libmagic1
ENV PYTHONUNBUFFERED 1
WORKDIR /scripts
RUN pip install req.txt
COPY scripts /scripts
