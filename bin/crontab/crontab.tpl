#
# {{ header }}
#

# MAILTO=some-email-list

HOME=/tmp

# Every minute!
* * * * * {{ cron }}

# Every hour.
42 * * * * {{ django }} cleanup

# Every 2 hours.
1 */2 * * * {{ cron }} something

# Etc...

MAILTO=root
