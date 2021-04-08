FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD [ "python", "main.py" ]
