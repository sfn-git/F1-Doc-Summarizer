FROM python:3.11-slim

RUN mkdir /app
ADD ./utils/*.py /app/utils/
ADD ./requirements.txt /app/requirements.txt
ADD ./*.py /app/
ADD ./web/*.py /app/web/
ADD ./web/templates /app/web/templates
WORKDIR /app

#Update System
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        default-jre cron
#Update pip
RUN pip install --upgrade pip
#Install Python Dependencies
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "main.py"]