# We use memcached in production, so we _should_ use it while
# we develop as well. That said, playdoh shouldn't *rely* on it
# entirely; it should work with any non-null cache store in Django.
class memcached {
    package { "memcached":
        ensure => installed;
    }

    service { "memcached":
        ensure => running,
        enable => true,
        require => Package['memcached'];
    }
}
