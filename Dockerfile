FROM python:3.10-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir "flask_app"
ENV FLASK_APP=flask_app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ADD flask_app flask_app
CMD [ "flask", "run" ]