#!/bin/sh
set -eux

BASE=$(cd $(dirname "$0") && pwd)
cd ${BASE}
source ./config
FP_BASE="${FLASHPOINT}/Arcade/Games/Flash"
APACHE2_VERSION="2.4.33"
PHP_VERSION="7.2.7"

rm -rv dl || true
rm -rv src || true
mkdir -p apache dl src
cd dl
cat << EOF > src_list
http://www.apache.org/dist/httpd/httpd-${APACHE2_VERSION}.tar.gz
http://php.net/distributions/php-${PHP_VERSION}.tar.xz
EOF

wget -i src_list
sha256sum -c ../sha256sums
for i in *.tar.*; do
	tar -xvf "$i" -C ../src;
done

# compile apache
cd "${BASE}/src/httpd-${APACHE2_VERSION}"
./configure --prefix="${BASE}/apache" --enable-asis --enable-cgi --enable-isapi --enable-ssl

# unlink htdocs symlink if exists to avoid clobbering
rm ${BASE}/apache/htdocs || true
make ${MAKEFLAGS}
make install

# compile php
cd "${BASE}/src/php-${PHP_VERSION}"
./configure --prefix="${BASE}/apache" --with-apxs2="${BASE}/apache/bin/apxs" --with-sqlite3=shared --with-pdo-sqlite=shared 
make ${MAKEFLAGS}
make install

# configure the apache installation
cd "${BASE}/apache"
# don't need default htdocs, delete and replace with flashpoint's
rm htdocs/index.html
rmdir htdocs
ln -s "${FP_BASE}/htdocs" htdocs

# copy over a bunch of configs that flashpoint apparently uses
cp "${FP_BASE}/conf/httpd.conf" conf/httpd.conf
cp "${FP_BASE}/conf/extra/httpd-ahssl.conf" conf/extra/httpd-ahssl.conf
rm -rv conf/ssl || true
cp -r "${FP_BASE}/conf/ssl" conf
cp "${FP_BASE}/php.ini" conf/php.ini

#mkdir -p lib/php/ext
#cp lib/php/extensions/**/*.so ext

# replace some things within the flashpoint config file

# write in srvroot, usually done by update_httpdconf_main_dir.php on windows
sed -i 's|^Define SRVROOT.*$|Define SRVROOT "'"${BASE}/apache"'"\r|' conf/httpd.conf
# fix the php module path
sed -i 's|php7apache2_4.dll|${SRVROOT}/modules/libphp7.so|' conf/httpd.conf
# enable the unixd module or apache won't start
sed -i 's|mod_xml2enc.so\r|mod_xml2enc.so\r\nLoadModule unixd_module modules/mod_unixd.so\r|' conf/httpd.conf

#sed -i 's|PHPIniDir ./|PHPIniDir ${SRVROOT}/conf|' conf/httpd.conf
# forget the shipped php ini i can't get sqlite to work with it, comment it out
sed -i 's|PHPIniDir|#PHPIniDir|' conf/httpd.conf
# make apache write logs to a useful place
sed -i 's|ErrorLog NUL|ErrorLog "${SRVROOT}/logs/error.log"|' conf/httpd.conf
# reeeeeeeee
#sed -i 's|extension_dir = "ext"|extension_dir = "'"${BASE}/lib/php/ext"'"|' conf/php.ini
