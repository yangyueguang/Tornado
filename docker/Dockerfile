FROM python3.7
MAINTAINER lihanqing@datagrand.com

ADD .ssh /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa
ADD requirements.txt /root/project_demo/
RUN cd /root/project_demo/ &&\
    pip install -r requirements.txt &&\
    rm ./requirements.txt && \
    rm -rf /root/.ssh

ADD ./start_server.py /root/project_demo/
ADD ./project_demo /root/project_demo/project_demo
WORKDIR /root/project_demo

ADD ./docker/setup.py /root/project_demo/project_demo/
RUN cd /root/project_demo/project_demo && python setup.py build_ext && rm ./setup.py

RUN mkdir /data/ && ln -s /root/project_demo/project_demo/log /data/log

EXPOSE 8080
CMD python start_server.py