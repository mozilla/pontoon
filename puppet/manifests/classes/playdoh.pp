# playdoh-specific commands that get playdoh all going so you don't
# have to.

# TODO: Make this rely on things that are not straight-up exec.
class playdoh {
    exec { "create_mysql_database":
        command => "/usr/bin/mysqladmin -uroot create $DB_NAME",
        unless  => "/usr/bin/mysql -uroot -B --skip-column-names -e 'show databases' | /bin/grep '$DB_NAME'",
    }

    exec { "grant_mysql_database":
        command => "/usr/bin/mysql -uroot -B -e'GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@localhost # IDENTIFIED BY \"$DB_PASS\"'",
        unless  => "/usr/bin/mysql -uroot -B --skip-column-names mysql -e 'select user from user' | /bin/grep '$DB_USER'",
        require => Exec["create_mysql_database"];
    }

    exec { "syncdb":
        cwd => "$PROJ_DIR",
        command => "/usr/bin/python2.6 ./manage.py syncdb --noinput",
        require => Exec["grant_mysql_database"];
    }

    exec { "sql_migrate":
        cwd => "$PROJ_DIR",
        command => "/usr/bin/python2.6 ./vendor/src/schematic/schematic migrations/",
        require => [
            Service["mysql"],
            Package["python2.6-dev", "libapache2-mod-wsgi", "python-wsgi-intercept" ],
            Exec["syncdb"]
        ];
    }
}
