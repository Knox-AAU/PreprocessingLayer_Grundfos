# Base Docker image (python ver. 3.8)
FROM python:3.8-slim-buster

# Install Git
RUN apt-get -y update
RUN apt-get -y install git

RUN pip install --upgrade pip

# Set up the work directory
WORKDIR /grundfos-preprocessing

# Install Ghostscript
RUN apt-get update
RUN apt-get -y install ghostscript

# Fix cv2 issue
RUN apt-get -y install python3-opencv

# Copy the requirements to the work directory
COPY requirements_nocuda.txt requirements_nocuda.txt

# Install Dependencies
RUN pip install --extra-index-url https://repos.knox.cs.aau.dk/ -r requirements_nocuda.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["segment.py", "-c"]