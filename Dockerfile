FROM docker.mci.dev/darkube/mci/gfs/python:3.11

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY manage.py /app
COPY runserver.sh /app
COPY run_event_processor.sh /app
COPY run_game_processor.sh /app
COPY run_general_processor.sh /app
COPY eagle_eyes /app/eagle_eyes

EXPOSE 8000

CMD ["./runserver.sh"]
