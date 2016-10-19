
# We need kstat, which should be at the same level as ourselves.
# Diamond will find it just fine, but tweaking the path here makes
# tests and other consumers easier.

from os import path
import sys

kstat_dir = '/'.join(path.realpath(__file__).split('/')[0:-2])
sys.path.append(kstat_dir + '/kstat')

from sunos_helpers import *
