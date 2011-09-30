# stage {"pre": before => Stage["main"]} class {'apt': stage => 'pre'}

# Commands to run before all others in puppet.
class init {
    group { "puppet":
        ensure => "present",
    }

    case $operatingsystem {
        ubuntu: {
            exec { "update_apt":
                command => "/usr/bin/sudo /usr/bin/apt-get update",
            }
        }
    }
}
