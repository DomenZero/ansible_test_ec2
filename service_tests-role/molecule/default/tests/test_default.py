import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_user(host):
    user = host.user("ec2-user")
    assert user.exists

def test_os_release(host):
    assert host.file("/var/www/html/index.html").contains("<!DOCTYPE html>")
    
@pytest.mark.parametrize('pkg', [
  'httpd',
  'firewalld'
])
def test_pkg(host, pkg):
    package = host.package(pkg)
    assert package.is_installed

@pytest.mark.parametrize('svc', [
  'httpd.service'
])
def test_svc(host, svc):
    service = host.service(svc)
    assert service.is_running
    
def test_listen_ip4(host):
    prt = host.socket("tcp://0.0.0.0:80")
    assert prt.is_listening
    
def test_listen_ssh(host):
    prt = host.socket("tcp://0.0.0.0:22")
    assert prt.is_listening