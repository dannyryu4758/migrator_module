FROM oraclelinux:7-slim
RUN  curl -o /etc/yum.repos.d/public-yum-ol7.repo https://yum.oracle.com/public-yum-ol7.repo && \
     yum-config-manager --enable ol7_oracle_instantclient && \
     yum -y install oracle-instantclient18.3-basic oracle-instantclient18.3-devel oracle-instantclient18.3-sqlplus && \
     rm -rf /var/cache/yum && \
     echo /usr/lib/oracle/18.3/client64/lib > /etc/ld.so.conf.d/oracle-instantclient18.3.conf && \
     ldconfig
ENV PATH=$PATH:/usr/lib/oracle/18.3/client64/bin    

FROM python:slim
COPY --from=0 /usr/lib/oracle/18.3/client64/lib /root/usr/lib/oracle/18.3/client64/lib
COPY --from=0 /usr/lib/oracle/18.3/client64/bin /root/usr/lib/oracle/18.3/client64/bin
ENV PATH=$PATH:/root/usr/lib/oracle/18.3/client64/bin:/root/usr/lib/oracle/18.3/client64/lib
ENV ORACLE_HOME=/root/usr/lib/oracle/18.3/client64/:$ORACLE_HOME
ENV LD_LIBRARY_PATH=/root/usr/lib/oracle/18.3/client64/:$LD_LIBRARY_PATH
RUN echo $PATH
RUN echo $ORACLE_HOME
RUN chmod 755 /root/usr/lib/oracle/18.3/client64/lib/*
RUN ls -l /root/usr/lib/oracle/18.3/client64/lib
COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/tracer_module
RUN python setup.py install
WORKDIR /app
