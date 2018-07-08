#!/bin/sh
set -eux

cd $(dirname "$0")

APACHE2_VERSION="2.4.33"
PHP_VERSION="7.2.7"

rm -rv dl || true

mkdir -p apache dl sources
cd dl
wget "http://www.apache.org/dist/httpd/httpd-${APACHE2_VERSION}.tar.gz"
wget "http://php.net/distributions/php-${PHP_VERSION}.tar.xz"
sha256sum -c ../sha256sums
cd ../sources
tar -xvf "../dl/httpd-${APACHE2_VERSION}.tar.gz"
tar -xvf "../dl/php-${PHP_VERSION}.tar.xz"
