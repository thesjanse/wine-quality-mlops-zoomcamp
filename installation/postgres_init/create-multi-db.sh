#!/bin/bash

set -e
set -u

function create_user_and_database() {
	local database=$1
	local password=$2
	echo "  Creating user and database '$database' with password  '$password'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $database WITH ENCRYPTED PASSWORD '$password';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
		user=$(echo $db | awk -F":" '{print $1}')
		pswd=$(echo $db | awk -F":" '{print $2}')
		if [[ -z "$pswd" ]]
		then
			pswd=$user
    	fi
		create_user_and_database $user $pswd
	done
	echo "Multiple databases created"
fi
