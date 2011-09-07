VERSION = (0, 9, 0, 'beta', 0)

short_names = {
  'alpha': 'a',
  'beta': 'b',
  'pre': 'pre',
  'final': '',
  'rc': 'rc'
}


def get_short_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    version = '%s%s' % (version,
                        short_names.get(VERSION[3], VERSION[3]))
    if VERSION[3] not in ('pre', 'final') and VERSION[4]:
        version = '%s%s' % (version, VERSION[4])
    return version

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3]:
        version = '%s %s' % (version, VERSION[3])
    if VERSION[3] not in ('pre', 'final') and VERSION[4]:
        version = '%s %s' % (version, VERSION[4])
    return version
