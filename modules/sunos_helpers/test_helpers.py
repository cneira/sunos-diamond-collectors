from os import path as p
import yaml

def read_fixture(includer, fixture):
    """
    Sometimes I can't use the supplied read fixture method because
    the test chokes on "Mock not being iterable" or related. Also,
    that method returns a string, and we are likely mocking the
    output of `sunos_helpers.run_cmd()` which returns a list of
    strings.

    args:
        includer: the file requesting a fixture must pass in its
            name. Required. (string)
        fixture: the name of the fixture file being requested.
            Required. (string)
    """

    with open(p.join(p.dirname(p.realpath(includer)), 'fixtures',
            fixture)) as fh:
        return fh.read().strip().split('\n')

def load_fixture(includer, fixture):
    """
    Returns a dict loaded from a fixture which is assumed to be a YAML
    file.
    """

    with open(p.join(p.dirname(p.realpath(includer)), 'fixtures',
            fixture)) as fh:
        return yaml.load(fh)
