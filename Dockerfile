FROM python:3.11-slim

RUN mkdir /app
ADD ./utils /app/utils
ADD ./requirements.txt /app/requirements.txt
ADD ./*.py /app/
WORKDIR /app

#Update System
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        default-jre
#Update pip
RUN pip install --upgrade pip
#Install Python Dependencies
RUN pip install -r requirements.txt

CMD ["python", "main.py"]