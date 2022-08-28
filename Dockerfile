FROM python:3.10-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir "/etc/flask_app"
#ENV FLASK_RUN_HOST=0.0.0.0
#ADD flask_app flask_app
WORKDIR /etc/flask_app
CMD [ "gunicorn", "--bind","0.0.0.0:5000","wsgi:app" ]