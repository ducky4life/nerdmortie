FROM arm64v8/python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ducky4life/nerdmortie"

COPY requirements.txt /

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt update && apt install -y ffmpeg

COPY /local /local

COPY nerdmortie.py downloader.py .env /

WORKDIR /

CMD [ "python", "nerdmortie.py" ]
