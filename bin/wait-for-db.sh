#!/bin/bash
# Wait for db container to be up and run a command.
set +e

test_sql() {
   PGPASSWORD=asdf psql -h db -U pontoon -d pontoon -c ";" -q >/dev/null 2>&1
}

tries=10
while ! test_sql; do
    (( tries -= 1 ))
    if (( $tries <= 0 )); then
        echo "Could not connect to db container, aborting."
        exit 1
    fi
    sleep 1
done

# Database is up, run the passed arguments as a command.
$*
