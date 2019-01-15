# See CKAN docs on installation from Docker Compose on usage
FROM debian:jessie
MAINTAINER Open Knowledge

# Internals
ENV CKAN_HOME /usr/lib/ckan
ENV CKAN_VENV ${CKAN_HOME}/venv
ENV SRC_DIR ${CKAN_VENV}/src
ENV CKAN_CONFIG /etc/ckan
ENV CKAN_INI ${CKAN_CONFIG}/production.ini
ENV PIP_SRC ${SRC_DIR}
ENV CKAN_STORAGE_PATH /var/lib/ckan

ENV GIT_URL=https://github.com/ckan/ckan.git

# CKAN version to build
#ENV GIT_BRANCH=ckan-2.8.1
ENV GIT_BRANCH=master

# Customize these on the .env file if needed
#ENV CKAN_SITE_URL http://localhost:5000
ENV CKAN__PLUGINS image_view text_view recline_view envvars scheming_datasets fluent aafc
ENV CKAN___SCHEMING__DATASET_SCHEMAS "ckanext.aafc:schemas/aafc_base_dataset.yaml ckanext.aafc:schemas/aafc_geospatial.yaml ckanext.aafc:schemas/aafc_open_gov_dataset.yaml ckanext.scheming:ckan_dataset.json"
ENV CKAN___SCHEMING__PRESETS "ckanext.scheming:presets.json ckanext.fluent:presets.json ckanext.aafc:schemas/tbs_presets.yaml"
ENV CKAN___SCHEMING__DATASET_FALLBACK=false
ENV CKAN__SEARCH__SHOW_ALL_TYPES=true
ENV CKAN__LOCALE_ORDER en fr
ENV CKAN__DATASET__CREATE_ON_UI_REQUIRES_RESOURCES=false

WORKDIR ${SRC_DIR}

# Install required system packages
RUN apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade \
    && apt-get -q -y install \
        python-dev \
        python-pip \
        python-virtualenv \
        python-wheel \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        build-essential \
        git-core \
        python-yaml \
        vim \
        wget \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# Build-time variables specified by docker-compose.yml / .env
ARG CKAN_SITE_URL

# Create ckan user
RUN useradd -r -u 900 -m -c "ckan account" -d $CKAN_HOME -s /bin/false ckan

# Setup virtual environment for CKAN
RUN mkdir -p $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH && \
    virtualenv $CKAN_VENV && \
    ln -s $CKAN_VENV/bin/pip /usr/local/bin/ckan-pip &&\
    ln -s $CKAN_VENV/bin/paster /usr/local/bin/ckan-paster

# Setup CKAN
#RUN pip install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan
RUN cd ${SRC_DIR} && git clone -b ${GIT_BRANCH} --single-branch ${GIT_URL}

RUN ckan-pip install -U pip && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirement-setuptools.txt && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirements.txt && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/dev-requirements.txt && \
    ckan-pip install -e $CKAN_VENV/src/ckan/ && \
    ln -s $CKAN_VENV/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini && \
    cp -v $CKAN_VENV/src/ckan/contrib/docker/ckan-entrypoint.sh /ckan-entrypoint.sh && \
    chmod +x /ckan-entrypoint.sh && \
    chown -R ckan:ckan $CKAN_HOME $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH

ENTRYPOINT ["/ckan-entrypoint.sh"]

USER ckan
EXPOSE $CKAN_PORT

RUN    . $CKAN_VENV/bin/activate && cd $CKAN_VENV/src && \
    pip install PyYAML && \
    pip install ckanapi && \
    pip install geojson && \
    pip install geomet && \
    pip install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming" && \
    pip install -r ./ckanext-scheming/requirements.txt && \
    pip install -e "git+https://github.com/ckan/ckanext-fluent.git#egg=ckanext-fluent" && \
    pip install -e "git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars" && \
    pip install -e "git+https://github.com/aafc-ckan/ckanext-aafc.git#egg=ckanext-aafc" && \
    chown -R ckan:ckan $CKAN_HOME $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH && \
# Create and update CKAN config
    paster --plugin=ckan make-config ckan ${CKAN_INI} && \
    paster --plugin=ckan config-tool ${CKAN_INI} "ckan.plugins = ${CKAN__PLUGINS}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "ckan.site_url = ${CKAN__SITE_URL}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "ckan.locale_order = ${CKAN__LOCALE_ORDER}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "scheming.dataset_schemas = ${CKAN___SCHEMING__DATASET_SCHEMAS}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "scheming.presets = ${CKAN___SCHEMING__PRESETS}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "scheming.dataset_fallback = ${CKAN___SCHEMING__DATASET_FALLBACK}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "ckan.search.show_all_types = ${CKAN__SEARCH__SHOW_ALL_TYPES}" && \
    paster --plugin=ckan config-tool ${CKAN_INI} "ckan.dataset.create_on_ui_requires_resources = ${CKAN__DATASET__CREATE_ON_UI_REQUIRES_RESOURCES}"

CMD ["ckan-paster","serve","/etc/ckan/production.ini"]
