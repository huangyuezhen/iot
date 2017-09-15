'''
'''
import sys

from common import util



sys.modules[__name__] = util.read_yaml('conf.d/serve.yml')

