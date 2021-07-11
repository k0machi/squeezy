CREATE USER squeezy IDENTIFIED BY 'squeezy';
CREATE DATABASE squeezydb;
GRANT ALL PRIVILEGES ON squeezydb.* TO 'squeezy'@'%';