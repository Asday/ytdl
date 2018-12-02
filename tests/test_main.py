from django.core.management import call_command


def test_server_starts(client):
    client.get('/')


def test_checks_pass():
    call_command('check')
