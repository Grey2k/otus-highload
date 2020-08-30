FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y gcc \
                       vim \
                       iputils-ping \
                       telnet \
                       curl \
                       git \
                       httpie \
                       nmap \
                       netcat && \
    apt-get clean

RUN apt-get install -y npm

WORKDIR /usr/src/

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD /usr/local/bin/gunicorn --worker-class aiohttp.GunicornUVLoopWebWorker -w 1 -b :8000 app.app:app --reload

