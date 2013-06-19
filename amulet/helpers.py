
import os
import yaml
import signal
import subprocess

from contextlib import contextmanager


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value


@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        print "Triggered signal handler"
        raise TimeoutError()
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class JujuVersion(object):
    def __init__(self, major=0, minor=0, patch=0, get_version=True):
        self.mapping = ['major', 'minor', 'patch']
        self.major = major
        self.minor = minor
        self.patch = patch

        if get_version:
            self.get_version()

    def parse_version(self, version_str):
        version = version_str.split()
        if len(version) > 1:
            version_str = version[1]
        else:
            version_str = version[0]

        return version_str.split('-')[0].split('.')

    def update_version(self, version_list):
        for i, ver in enumerate(version_list):
            try:
                setattr(self, self.mapping[i], int(ver))
            except:
                break  # List out of range? Versions not semantic? Too bad

    def get_version(self):
        cmd = ['juju', 'version']
        try:
            version = subprocess.check_output(cmd)
        except:
            cmd[1] = '--version'
            version = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        self.update_version(self.parse_version(version))

    def __str__(self):
        return '.'.join(str(v) for v in [self.major, self.minor, self.patch])

JUJU_VERSION = JujuVersion()

def environments(juju_home="~/.juju/"):
    env_file = os.path.expanduser(os.path.join(juju_home, 'environments.yaml'))
    if not os.path.isfile(env_file):
        raise IOError('%s was not found.' % env_file)

    with open(env_file, 'r') as env_yaml:
        envs = yaml.safe_load(env_yaml.read())

    return envs

def default_environment(juju_home="~/.juju/"):
    envs = environments(juju_home)
    if 'default' in envs:
        return envs['default']
    else:
        if len(envs['environments']) != 1:
            raise ValueError('No default environment specified.')

        return envs['environments'].itervalues().next()
