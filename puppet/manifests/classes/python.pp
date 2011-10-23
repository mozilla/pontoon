# Install python and compiled modules for project
class python {
    case $operatingsystem {
        centos: {
            package {
                ["python26-devel", "python26-libs", "python26-distribute", "python26-mod_wsgi"]:
                    ensure => installed;
            }

            exec { "pip-install":
                command => "easy_install -U pip",
                creates => "pip",
                require => Package["python26-devel", "python26-distribute"]
            }

            exec { "pip-install-compiled":
                command => "pip install -r $PROJ_DIR/requirements/compiled.txt",
                require => Exec['pip-install']
            }
        }

        ubuntu: {
            package {
                ["python2.6-dev", "python2.6", "libapache2-mod-wsgi", "python-wsgi-intercept", "python-pip"]:
                    ensure => installed;
            }

            exec { "pip-install-compiled":
                command => "pip install -r $PROJ_DIR/requirements/compiled.txt",
                require => Package['python-pip']
            }
        }
    }
}
