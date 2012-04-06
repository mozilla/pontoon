#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

$PROJ_DIR = "/home/vagrant/project"

# You can make these less generic if you like, but these are box-specific
# so it's not required.
$DB_NAME = "playdoh_app"
$DB_USER = "root"

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

class dev {
    class {
        init: before => Class[mysql];
        mysql: before  => Class[python];
        python: before => Class[apache];
        apache: before => Class[playdoh];
        memcached: ;
        playdoh: ;
        custom: ;
    }
}

include dev
