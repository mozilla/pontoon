from ..core import Package, Structure, EntityList, Blob, Entity
from .clients import IOClient, DBClient

import os
import MySQLdb
import re

def register(Manager):
    Manager.register(MysqlClient)

class MysqlClient(DBClient):
    name = 'mysql'
    desc = "MySQL reader/writer"
    type = IOClient.__name__
    connection = None

    @classmethod
    def matches_path(cls, path):
        """
        tests if the ioclient should be used for this type of path
        Matches any mysql://
        """
        print path
        return path.startswith('mysql://')

    @classmethod
    def get_entitylist(cls, path, source=False, code='default', parser=None):
        entitylist = EntityList()
        # we should reduce the number of explodes (it happens here and in connect)
        con = cls._connected()
        if not con:
            (host, port, db, user, password, table) = cls._explode_path(path)
            cls._connect(path)
        else:
            table = path
        entitylist.id = table
        cursor = cls.connection.cursor()
        cursor.execute('SELECT * FROM '+table)
        for row in cursor:
            entitylist.add_entity(Entity(row[0],row[1]))
        cursor.close()
        if not con:
            cls._close()
        return entitylist

    @classmethod
    def get_l10npackage(cls, path,
                        code='default',
                        object_type='l10nobject',
                        source=None,
                        ignore=['CVS','.svn','.DS_Store', '.hg']):
        l10npackage = L10nPackage()
        cls._connect(path)
        cursor = cls.connection.cursor()
        cursor.execute('SHOW TABLES')
        for row in cursor:
            elist = cls.get_entitylist(row[0])
            l10npackage.add_object(elist)
        cursor.close()
        cls._close()
        return l10npackage

    @classmethod
    def write_entitylist(cls, elist, path, encoding=None):
        con = cls._connected()
        if not con:
            cls._connect(path)

        table = elist.id
        cursor = cls.connection.cursor()
        cursor.execute('DELETE FROM '+table)
        l = [(e.id, e.get_value()) for e in elist.values()]
        cursor.executemany("""INSERT INTO """+table+""" (id, value)
                          VALUES (%s, %s)""",
                          l)
        if not con:
            cls._close()
        return True

    @classmethod
    def write_l10npackage(cls, l10npack, path):
        cls._connect(path)
        for i in l10npack.objects:
            cls.write_entitylist(l10npack.objects[i], path)
        cls._close()
        return True

    @classmethod
    def path_type(cls, path):
        """
        returns 'package', 'object' depending on the path type
        """
        (host, port, db, user, password, table) = cls._explode_path(path)
        if not table:
            return 'package'
        else:
            return 'object'

#=======================================

    @classmethod
    #mysql://localhost/db?user=foo&password=foo2
    def _explode_path(cls, path):
        pattern = re.compile('^mysql://([^:\/]+):?([0-9]+)?\/?([^\?]+)?\??(.+)?')
        match = pattern.match(path)
        if match:
            host = match.group(1)
            port = match.group(2) or False
            db = match.group(3)
            params = {}
            s = match.group(4)
            if s:
                for i in s.split('&'):
                    pair = i.split('=')
                    key = pair[0].strip()
                    val = pair[1].strip()
                    params[key] = val
            user = params.get('user') or ''
            password = params.get('password') or ''
            table = params.get('table') or None
            return (host, port, db, user, password, table)
        else:
            raise Exception('path is not parseable')

    @classmethod
    def _connect(cls, path):
        if not cls._connected():
            (host, port, db, user, password, table) = cls._explode_path(path)
            cls.connection = MySQLdb.connect(host = host,
                                        port = port,
                                        user = user,
                                        passwd = password,
                                        db = db,
                                        use_unicode = True)

    @classmethod
    def _close(cls):
        if cls._connected():
            cls.connection.close()
            cls.connection = None

    @classmethod
    def _connected(cls):
        return bool(cls.connection)