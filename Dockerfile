FROM python:3.7-slim

RUN mkdir /app
ADD . /app
WORKDIR /app

# Download Chrome Dependecies
RUN apt-get update
RUN apt-get -y install wget unzip
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm ./google-chrome-stable_current_amd64.deb
RUN wget -q https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN rm chromedriver_linux64.zip*

RUN pip install requests
RUN pip install selenium

CMD ["python", "main.py"]