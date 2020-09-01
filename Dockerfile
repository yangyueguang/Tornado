FROM python:3.7
MAINTAINER xuechao@datagrand.com
LABEL maintainer="2829969299@qq.com"
LABEL description="tornado project"
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV zip_url="https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip"
ENV zip_name="instantclient-basic-linux.x64-19.5.0.0.0dbru.zip"
RUN mkdir -p /opt/oracle && cd /opt/oracle/ \
 && wget -c $zip_url && unzip $zip_name \
 && apt-get update && apt-get install -y libaio1 && apt-get clean
ENV LD_LIBRARY_PATH /opt/oracle/instantclient_19_5:$LD_LIBRARY_PATH

# 1. install ssh 这样可以支持远程debug
RUN apt-get update && apt-get -y install openssh-server
RUN mkdir -p /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile


COPY .ssh /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa

ADD app /app
COPY scripts/requires.txt /app/
RUN cd /app && pip install -r requires.txt
WORKDIR /app
VOLUME /app/static
EXPOSE 8000
CMD /usr/sbin/sshd -D
ENTRYPOINT python app.py
