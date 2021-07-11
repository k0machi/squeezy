FROM fedora:34
RUN dnf install -y nodejs npm python3 python3-devel python3-wheel python3-virtualenv python3-pip\
     mariadb mariadb-connector-c mariadb-connector-c-devel mariadb-common mariadb-server \
     git gcc g++ libstdc++ \
     squid supervisor nginx uwsgi uwsgi-plugin-python3
RUN npm install -g yarn
RUN /usr/libexec/mariadb-prepare-db-dir
WORKDIR /app
COPY . /app/
RUN ./mariadb_init.sh
RUN yarn install
RUN pip install -r ./requirements.txt
RUN yarn webpack
RUN python3 ./basic_config.py
RUN chown root:nginx -R /app
RUN chmod u=rwX,g=rwX,o=rX -R /app
RUN cp /app/config/squeezy-nginx.conf /etc/nginx/nginx.conf
RUN cp /app/config/uwsgi_params /etc/nginx/
RUN chown nginx:nginx -R /etc/squid /var/log/squid /var/spool/squid
CMD ["/usr/bin/supervisord", "-c", "/app/config/supervisord.conf", "-n", "-l", "/app/logs/supervisord.log"]
