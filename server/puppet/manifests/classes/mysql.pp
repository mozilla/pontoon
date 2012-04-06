# Get mysql up and running
class mysql {
    package { "mysql-server":
        ensure => installed;
    }

    case $operatingsystem {
        centos: {
            package { "mysql-devel":
                ensure => installed;
            }
        }

        ubuntu: {
            package { "libmysqld-dev":
                ensure => installed;
            }
        }
    }

    service { "mysql":
        ensure => running,
        enable => true,
        require => Package['mysql-server'];
    }
}
