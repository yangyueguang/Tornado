FROM python:3.7
MAINTAINER xuechao@datagrand.com
ENV NAME="output_extract"
ADD app /app
COPY scripts/requires.txt /app/
RUN cd /app && pip install -r requires.txt
WORKDIR /app
VOLUME /app/static
EXPOSE 8081
CMD echo 'a'
ENTRYPOINT python app.py