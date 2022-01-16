FROM python:3.7-slim
ENV APP_HOME /contact-api-internal
WORKDIR $APP_HOME
COPY . ./
RUN pip install -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker contact-api-internal.main:app
