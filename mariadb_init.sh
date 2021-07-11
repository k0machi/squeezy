#!/bin/bash
# Initialize MariaDB
/usr/libexec/mariadbd --user=root --basedir=/usr &

until mariadb-admin ping >/dev/null 2>&1; do
  echo -n "."; sleep 0.2
done

mariadb < init_db.sql

mariadb-admin shutdown

chown mysql:mysql -R /var/lib/mysql