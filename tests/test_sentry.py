import unittest
import yaml

from amulet.sentry import Talisman, UnitSentry
from mock import patch



class TalismanTest(unittest.TestCase):
    # Mock the Juju Status Output
    JUJU_STATUS = '''
    environment: local
    machines:
      "0":
        agent-state: started
        agent-version: 1.17.2.1
        dns-name: localhost
        instance-id: localhost
        series: saucy
      "1":
        agent-state: started
        agent-version: 1.17.2.1
        dns-name: 10.0.3.175
        instance-id: charles-local-machine-1
        series: precise
        hardware: arch=amd64
    services:
      postgresql:
        charm: cs:precise/postgresql-61
        exposed: false
        relations:
          replication:
          - postgresql
        units:
          postgresql/0:
            agent-state: started
            agent-version: 1.17.2.1
            machine: "1"
            open-ports:
            - 5432/tcp
            public-address: 10.0.3.175
      relation-sentry:
        charm: cs:precise/relation-sentry-1
        exposed: false
        units:
          relation-sentry/0:
            agent-state: started
            agent-version: 1.17.2.1
            machine: "1"
            public-address: 10.0.3.176'''

    @patch('amulet.sentry.waiter.status')
    @patch('amulet.sentry.requests')
    def test_talisman_wait(self, mockUnitSentry, mockStatus):
        mockStatus.return_value = yaml.load(self.JUJU_STATUS)
        x = mockUnitSentry.return_value
        x.get.return_value.json.return_value = {'hook': 'install'}

        t = Talisman(['postgresql'], juju_env="local")
        mockStatus.assert_called_with("local")
        t.wait(1)
        x.get.assert_called_with("10.0.3.175")
