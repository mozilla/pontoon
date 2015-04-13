#!/bin/bash
run_sql() {
   mysql -h"db" -uroot -p"asdf" -D"pontoon" -e "$1"
}

# Set the database to use UTF-8 for everything.
run_sql 'ALTER DATABASE pontoon CHARACTER SET utf8'
