VERSION = (0, 11, 2, "", 0)

short_names = {"alpha": "a", "beta": "b", "pre": "pre", "final": "", "rc": "rc"}


def get_short_version():
    version = "{}.{}".format(VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "{}.{}".format(version, VERSION[2])
    version = "{}{}".format(version, short_names.get(VERSION[3], VERSION[3]))
    if VERSION[3] not in ("pre", "final") and VERSION[4]:
        version = "{}{}".format(version, VERSION[4])
    return version


def get_version():
    version = "{}.{}".format(VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "{}.{}".format(version, VERSION[2])
    if VERSION[3]:
        version = "{} {}".format(version, VERSION[3])
    if VERSION[3] not in ("pre", "final") and VERSION[4]:
        version = "{} {}".format(version, VERSION[4])
    return version
