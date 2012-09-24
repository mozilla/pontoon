VERSION = (0, 7, 0, 'alpha', 0)

def get_short_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] == 'alpha':
        version = '%sa' % version
    if VERSION[3] == 'beta':
        version = '%sb' % version
    if VERSION[3] == 'rc':
        version = '%sc' % version
    if VERSION[3] != 'final' and VERSION[4]:
            version = '%s%s' % (version, VERSION[4])
    return version

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        version = '%s %s' % (version, VERSION[3])
        if VERSION[3] != 'final':
            version = '%s %s' % (version, VERSION[4])
    return version
