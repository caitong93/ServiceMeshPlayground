FROM python:3

COPY . /usr/src/app
COPY pip.conf /root/.pip/pip.conf

WORKDIR /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./loadgen.py" ]