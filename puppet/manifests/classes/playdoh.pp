# playdoh-specific commands that get playdoh all going so you don't
# have to.

# TODO: Make this rely on things that are not straight-up exec.
class playdoh {
    file { "$PROJ_DIR/settings/local.py":
        ensure => file,
        source => "$PROJ_DIR/settings/local.py-dist",
        replace => false;
    }

    exec { "create_mysql_database":
        command => "mysql -uroot -B -e'CREATE DATABASE $DB_NAME CHARACTER SET utf8;'",
        unless  => "mysql -uroot -B --skip-column-names -e 'show databases' | /bin/grep '$DB_NAME'",
        require => File["$PROJ_DIR/settings/local.py"]
    }

    exec { "grant_mysql_database":
        command => "mysql -uroot -B -e'GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@localhost # IDENTIFIED BY \"$DB_PASS\"'",
        unless  => "mysql -uroot -B --skip-column-names mysql -e 'select user from user' | grep '$DB_USER'",
        require => Exec["create_mysql_database"];
    }

    exec { "syncdb":
        cwd => "$PROJ_DIR",
        command => "python ./manage.py syncdb --noinput",
        require => Exec["grant_mysql_database"];
    }

    exec { "sql_migrate":
        cwd => "$PROJ_DIR",
        command => "python ./vendor/src/schematic/schematic migrations/",
        require => [
            Service["mysql"],
            Package["python2.6-dev", "libapache2-mod-wsgi", "python-wsgi-intercept" ],
            Exec["syncdb"]
        ];
    }
}
