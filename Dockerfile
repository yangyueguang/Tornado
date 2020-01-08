FROM python:3.7
MAINTAINER xuechao@datagrand.com
ADD app /app
COPY scripts/requires.txt /app/
RUN cd /app && pip install -r requires.txt
WORKDIR /app
EXPOSE 8081
CMD python app.py