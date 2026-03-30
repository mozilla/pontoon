# Maintenance

The following describes tricks and tools useful for debugging and maintaining a production instance of Pontoon.

## Mitigating DDoS attacks

In a [DDoS attack](https://en.wikipedia.org/wiki/Denial-of-service_attack), the incoming traffic flooding the victim originates from many different sources. This stops everyone else from accessing the website as there is too much traffic flowing to it.

One way to mitigate DDoS attacks is to enable traffic throttling. Set the `THROTTLE_ENABLED` environment variable to `True` and configure other `THROTTLE*` variables to limit the number of requests per period from a single IP address.

A more involved but also more controlled approach is to identify the IP addresses of the attackers (see the handy [IP detection script](https://github.com/mozilla-l10n/pontoon-scripts/blob/main/dev/check_ips_heroku_log.py) to help with that) and block them. Find the attacking IP addresses in the Log Management Add-On (Papertrail) and add them to the `BLOCKED_IPS` environment variable.
