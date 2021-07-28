#!/bin/bash

# Build Apache 2.4.41 from Source

export HTTPD_VERSION=2.4.41
export DIR_TEMP=/app/temp
export DIR_BASE=/app
export DIR_INSTALL=$DIR_BASE/apache

yum -y install curl gcc make gcc-c++ expat-devel
mkdir -p $DIR_TEMP $DIR_INSTALL; rm -rf $DIR_TEMP/*; cd $DIR_TEMP && curl http://apache.mirror.rafal.ca//httpd/httpd-${HTTPD_VERSION}.tar.gz | tar -zxf -
curl http://us.mirrors.quenda.co/apache/apr/apr-1.7.0.tar.gz | tar -zxf - && mv apr-1.7.0 httpd-${HTTPD_VERSION}/srclib/apr
curl http://us.mirrors.quenda.co/apache//apr/apr-util-1.6.1.tar.gz | tar -zxf - && mv apr-util-1.6.1 httpd-${HTTPD_VERSION}/srclib/apr-util
curl curl ftp://ftp.pcre.org/pub/pcre/pcre-8.42.tar.gz | tar -zxf - && pushd pcre-8.42 && ./configure --prefix=$DIR_BASE/pcre;make;make install; popd
cd httpd-${HTTPD_VERSION} && ./configure --with-pcre=$DIR_BASE/pcre --prefix=$DIR_BASE/apache; make; make install

