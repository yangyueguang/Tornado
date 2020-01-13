FROM python:3.7
MAINTAINER xuechao@datagrand.com

LABEL maintainer="xuechao@datagrand.com"
LABEL description="guotaijunan project"
#ENV zip_url="https://download.oracle.com/otn_software/mac/instantclient/193000/instantclient-basic-macos.x64-19.3.0.0.0dbru.zip"
ENV zip_url="https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip"
#ENV zip_name="instantclient-basic-macos.x64-19.3.0.0.0dbru.zip"
ENV zip_name="instantclient-basic-linux.x64-19.5.0.0.0dbru.zip"
RUN mkdir -p /opt/oracle && cd /opt/oracle/ \
 && wget -c $zip_url \
 && unzip $zip_name \
 && apt-get update && apt-get install -y libaio1 && apt-get clean

ENV LD_LIBRARY_PATH /opt/oracle/instantclient_19_5:$LD_LIBRARY_PATH

ENV NAME="output_extract"
ADD app /app
COPY scripts/requires.txt /app/
RUN cd /app && pip install -r requires.txt
WORKDIR /app
VOLUME /app/static
EXPOSE 8000
CMD echo 'a'
ENTRYPOINT python app.py