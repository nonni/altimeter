from __future__ import with_statement
from fabric.api import *
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib.console import confirm
import datetime

env.hosts = []
date_str = datetime.datetime.now().strftime('%Y%m%d')

def pull():
    print(blue('Pulling git repository...'))
    local('git pull')

def pack():
    print(blue('Tarring source code'))
    local('tar czf /tmp/altimeter_%s.tar.gz *' % date_str)

def prepare_deploy():
    print(blue('Preparing for deployment'))
    pull()
    pack()

def deploy(user='eva', deployment_dir='/var/opt/eva/model/'):
    print(blue('Shipping code..'))
    put('/tmp/altimeter_%s.tar.gz' % date_str, '/tmp/')
    sudo('mkdir -p %s/altimeter' % deployment_dir, user=user)
    with cd(deployment_dir+'/altimeter'):
        print(blue('Deploying...'))
        #Cleanup old code
        sudo('rm -rf *', user=user)
        #Deploy new code.
        sudo('tar xzf /tmp/altimeter_%s.tar.gz' % date_str, user=user)

def cleanup():
    print(blue('Cleaning up..'))
    local('rm /tmp/altimeter_%s.tar.gz' % date_str)
    run('rm /tmp/altimeter_%s.tar.gz' % date_str)


def start_deployment(host, user='eva', deployment_dir='/var/opt/eva/model'):
    env.hosts.append(host)
    prepare_deploy()
    deploy(user=user, deployment_dir=deployment_dir)
    cleanup()

