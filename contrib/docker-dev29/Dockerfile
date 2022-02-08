FROM ubuntu:20.04

#ARG SITE_URL=http://localhost.localdomain
ARG SITE_URL=http://localhost
ARG ROOT_PATH=
ARG ALL_PASSWORD=welcome1
ARG GIT_TAG=master

ENV DEBIAN_FRONTEND=noninteractive
ENV TMP=/app/temp
ENV APP=/app/ckan/venv
ENV CKCF=/app/ckan/config/dev.ini
ENV ENV_GIT_TAG=${GIT_TAG}
ENV SOLR=/app/ckan/solr/bin/solr

# Prepare OS
RUN mkdir -p /app/ckan/admin /app/ckan/data
RUN apt update && apt install -y gnupg2 curl wget && \
    apt install -y apache2 postgresql-12 postgresql-12-postgis-3 libapache2-mod-wsgi redis-server ssh && \
    apt install -y vim git zip unzip pkg-config expect dos2unix openssh-server telnet && \
    apt install -y gcc make g++ automake linux-headers-generic && \
    apt install -y build-essential gettext musl-dev openjdk-8-jdk uwsgi uwsgi-plugins-all libtool libpq5 libpq-dev && \
    apt install -y python3-dev python3-pip python3-venv git-core python-is-python3 solr-jetty && \
    apt install -y libpq5 redis-server nginx supervisor
RUN ln -s /usr/lib/postgresql/12/bin/pg_ctl /usr/bin/pg_ctl

RUN mkdir -p $APP/src $TMP /app/ckan/config /app/ckan/log && \
    curl -o $TMP/getpip.py https://bootstrap.pypa.io/get-pip.py && python3 $TMP/getpip.py && \
    pip install pastescript && pip install pastedeploy && pip install supervisor && pip install "virtualenv==16.7.9" && \
    mkdir /etc/supervisord.d
RUN TZ=America/Toronto; ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN virtualenv $APP
COPY *.sh /app/ckan/admin/
# COPY ckan.service /etc/systemd/system/ && \
COPY ckan.conf /etc/apache2/conf-enabled/
RUN sed -i 's@###SITE_URL#@'"$SITE_URL"'@g' /etc/apache2/conf-enabled/ckan.conf
RUN sed -i 's@###ROOT_PATH#@'"$ROOT_PATH"'@g' /etc/apache2/conf-enabled/ckan.conf
RUN sed -i '1 i\LoadModule headers_module /usr/lib/apache2/modules/mod_headers.so' /etc/apache2/conf-enabled/ckan.conf
RUN sed -i '1 i\LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so' /etc/apache2/conf-enabled/ckan.conf
RUN sed -i '1 i\LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so' /etc/apache2/conf-enabled/ckan.conf
RUN sed -i '/httpd$/c\apachectl start' /app/ckan/admin/ckan.sh && sed -i '/httpd -k/c\apachectl stop' /app/ckan/admin/ckan.sh

# Database
RUN mkdir -p /app/ckan/pgdata /run/postgresql && chown -R postgres:postgres /app/ckan/pgdata /run/postgresql && \
    su - postgres -c "pg_ctl -D /app/ckan/pgdata init; echo \"listen_addresses = '*'\" >> /app/ckan/pgdata/postgresql.conf; pg_ctl -D /var/lib/postgresql/10/main stop; pg_ctl -w -D /app/ckan/pgdata start" && \
    su - postgres -c "psql -c \"create user ckan with password '"${ALL_PASSWORD}"';\"" && \
    su - postgres -c "psql -c \"CREATE DATABASE ckan WITH owner=ckan template=template0 encoding='UTF8';\"" && \
    su - postgres -c "psql -c \"alter user ckan createdb;\"" && \
    su - postgres -c "psql -d ckan -c \"create extension postgis; ALTER VIEW geometry_columns OWNER to ckan; ALTER TABLE spatial_ref_sys OWNER to ckan;\" " && \
    su - postgres -c "psql -c \"create user ckan_datastore with password '"${ALL_PASSWORD}"';create user ckan_datastore_ro with password '"${ALL_PASSWORD}"';\"" && su - postgres -c "psql -c \"CREATE DATABASE ckan_datastore WITH owner=ckan_datastore template=template0 encoding='UTF8';\"" && su - postgres -c "psql -c \"alter user ckan_datastore createdb;grant connect on database ckan_datastore to ckan_datastore_ro; \""  && \ 
    echo "host    all  all  0.0.0.0/0        md5" >> /app/ckan/pgdata/pg_hba.conf && echo "host    all  all  ::/0             md5" >> /app/ckan/pgdata/pg_hba.conf && \
    date

# CKAN
RUN . $APP/bin/activate && cd $APP/src && pip install setuptools==44.1.0 && pip install --upgrade pip && \
    pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.9.5#egg=ckan[requirements,dev]' && \
    pip install -r /app/ckan/venv/src/ckan/dev-requirements.txt && \
    pip install Shapely vdm ckantoolkit geoalchemy2 && \
    pip install -e git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    pip install ckanapi && pip install geojson && pip install geomet && \
    deactivate && . $APP/bin/activate && \
    cd $APP/src/ckan && cp who.ini /app/ckan/config/ && \
    #pip install -e "git+https://
	.com/aafc/ckanext-scheming.git#egg=ckanext-scheming" && \
    pip install -e git+https://github.com/ckan/ckanext-fluent.git#egg=ckanext-fluent && \
    pip install -e git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial && \
    pip install -r /app/ckan/venv/src/ckanext-spatial/pip-requirements.txt && \
    pip install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    pip install -r /app/ckan/venv/src/ckanext-harvest/pip-requirements.txt && \
    pip install -e git+https://github.com/ckan/ckanext-geoview.git#egg=ckanext-geoview && \
    pip install -r /app/ckan/venv/src/ckanext-geoview/pip-requirements.txt && \
    pip install -e git+https://gitlab.com/aafc/ckanext-aafcesas.git#egg=ckanext-aafcesas && \
    ckan generate config ${CKCF} && \
    ckan config-tool ${CKCF} "ckan.site_url = ${SITE_URL}" && \
    ckan config-tool ${CKCF} "ckan.root_path = ${ROOT_PATH}" && \
    ckan config-tool ${CKCF} "ckan.locale_order=en fr" && \
    ckan config-tool ${CKCF} "ckan.locales_offered=en fr" && \
    ckan config-tool ${CKCF} "ckan.storage_path=/app/ckan/data" && \
    echo "${SITE_URL}" && sed -E -i -e 's/sqlalchemy.url(.*)$/sqlalchemy.url = postgresql:\/\/ckan:'"${ALL_PASSWORD}"'@localhost:5432\/ckan/g' $CKCF && \
    sed -E -i -e 's/\#solr_url.*/solr_url = http:\/\/localhost:8983\/solr\/ckan/g' $CKCF &&  \
    sed -E -i -e 's/\#ckan.redis.url.*/ckan.redis.url = redis:\/\/localhost:8082\/0/g' $CKCF && grep ckan.site_url $CKCF
RUN . /app/ckan/venv/bin/activate && cd $APP/src/ckan && \
    ckan config-tool ${CKCF} -s handler_file "class = logging.handlers.RotatingFileHandler" && \
    ckan config-tool ${CKCF} -s handler_file "formatter = generic" && \
    ckan config-tool ${CKCF} -s handler_file "level = INFO" && \
    ckan config-tool ${CKCF} -s handler_file 'args = ("/app/ckan/log/ckan.log", "a", 20000000, 9)'  && \
    ckan config-tool ${CKCF} -s handlers "keys = console, file"  && \
    ckan config-tool ${CKCF} -s handlers "keys = console, file"  && \
    ckan config-tool ${CKCF} -s logger_ckan "handlers = console, file"  && \
    ckan config-tool ${CKCF} -s logger_ckanext "handlers = console, file"  && \
    ckan config-tool ${CKCF} "ckan.datastore.write_url=postgresql://ckan_datastore:${ALL_PASSWORD}@localhost:5432/ckan_datastore" && \
    ckan config-tool ${CKCF} "ckan.datastore.read_url=postgresql://ckan_datastore_ro:${ALL_PASSWORD}@localhost:5432/ckan_datastore" && \
    pip install paste pastedeploy && \
    date
    
# Apache SOLR
RUN adduser --disabled-password --gecos "" --shell /bin/bash ckan && \
    cd /app/ckan && curl https://archive.apache.org/dist/lucene/solr/8.11.1/solr-8.11.1.tgz | tar -zxf - && ln -sfn $PWD/solr-8.11.1 /app/ckan/solr && chown -R ckan /app/ckan/solr-8.11.1 /app/ckan/log
RUN su - ckan -c "$SOLR start && cd /app/ckan/solr && bin/solr create -c ckan"
RUN cd /app/ckan/solr/server/solr/ckan/conf/ && ln -sf /app/ckan/venv/src/ckan/ckan/config/solr/schema.xml ./schema.xml && rm managed-schema && \
  sed -i '/defaultSearchField/d' schema.xml &&  sed -i '/solrQueryParser/c\\<df\>text\<\/df\>\<solrQueryParser q.op="AND"\/\>' schema.xml && \
  sed -i '/<updateProcessor.*class="solr.AddSchemaFieldsUpdateProcessorFactory".*i/,/<\/updateProcessor>/d' solrconfig.xml && \
  sed -i '/<updateRequestProcessorChain.*add-unknown-fields-to-the-schema.*/,/<\/updateRequestProcessorChain>/d' solrconfig.xml && \
  sed -i '/<initParams.*/,/<\/initParams>/d' solrconfig.xml && sed -i '/<\/config>/i <schemaFactory class="ClassicIndexSchemaFactory"/>' solrconfig.xml
RUN su - ckan -c "$SOLR stop"; su - ckan -c "$SOLR start"

# Init
#RUN su - postgres -c "pg_ctl -w -D /app/ckan/pgdata start" && su - ckan -c "$SOLR start" && su - ckan -c "redis-server --port 8082 &" && \
#    . $APP/bin/activate && cd $APP/src/ckan && ckan -c $CKCF db init
#RUN . /app/ckan/venv/bin/activate && cd $APP/src/ckan && \
#    ckan config-tool ${CKCF} "ckan.plugins = envvars image_view text_view recline_view datastore fluent spatial_metadata spatial_query resource_proxy geo_view geojson_view wmts_view" && \
#    ckan config-tool ${CKCF} "scheming.presets=ckanext.scheming:presets.json ckanext.fluent:presets.json ckanext.aafc:schemas/tbs_presets.yaml ckanext.aafc:schemas/aafc_presets.yaml" && \
#    ckan config-tool ${CKCF} "scheming.dataset_schemas=ckanext.aafc:schemas/aafc_wg.yaml"

COPY *.exp /app/ckan/venv/src/ckan/
RUN sed -i "s/###ALL_PASSWORD#/${ALL_PASSWORD}/g" /app/ckan/venv/src/ckan/ckan-admin.exp
RUN dos2unix /app/ckan/admin/*.sh /app/ckan/venv/src/ckan/*.exp
RUN chmod +x /app/ckan/admin/*.sh /app/ckan/venv/src/ckan/*.exp

RUN cd /root; mkdir -p .ssh; touch .ssh/authorized_keys; chown -R root .ssh; chmod 700 .ssh; cd .ssh; chmod 600 authorized_keys && \
    echo "ssh-rsa xxxx" >>authorized_keys
RUN sed -i '/PermitRootLogin/a PermitRootLogin yes' /etc/ssh/sshd_config

EXPOSE 80 5000 2222

# Start CKAN
ENTRYPOINT ["/app/ckan/admin/ckan.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
