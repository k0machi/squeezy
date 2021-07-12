# Squeezy - Squid Config Management Made Easy

## Brief

Squeezy is a web application aimed to simplify managing of a Squid caching proxy. It does that by exposing squid configuration file as a set of primitives inside its Web User interface, managing squid instance by itself and by bundling everything into a single, ready to deploy container.

## Installation

Squeezy requires following conditions to be met:

* `git` must be present on the system
* `docker` must be present and available to current user

To install squeezy, simply download the bootstrap.py script, make it executable and run it:

```bash
curl -sSL https://raw.githubusercontent.com/k0machi/squeezy/master/bootstrap.py -o bootstrap.py
chmod +x bootstrap.py
./bootstrap.py
```

You can view available deploy options by executing `./bootstrap.py -h`

## Usage

By default, squeezy exposes `3128` tcp port for the proxy itself and `8080` tcp port for the web management UI. The default credentials are `admin@localhost` and `admin`.
It is advisable to either use host networking in docker, or adding an ACL to allow docker container network (whatever it may be on your machine) to access squid proxy (Default docker ip range is `172.17.0.0/16`).

To define squid directives, head into `DIRECTIVES` section of the web interface, to define ACLs head into `ACCESS CONTROL LISTS` section. If you need to upload a file for certain ACLs to be read - head into `FILES` section. After making changes, be sure to first hit the "Apply Configuration" button to generate `squid.conf`, and then hit `Reload Service` button to force squid to re-read its configuration file and restart.

## License

BSD-3-Clause, see [LICENSE](LICENSE)