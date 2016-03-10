
# 10mar16

- replace memcached with redis; test recipe, of course
- straighten up git repo
- check jay's pull request; refactoring usefull for my stuff
- rotate logs; straighten up logs
- readme in cadash repo


# 04mar16

- IN PROGRESS 10mar16: recipes to install/deploy in ec2/opsworks
- DONE 10mar16: meio-de-campo with sysops about ca tools
    * miguel says consolidate info on ca's is good
    * sysops has not spent a lot of time thinking what "handoff ca" means
- IN PROGRESS 10mar16: move from memcached to redis
- start porting ca-stats?
- jay to help with db (elastic search)


# 29feb16

- DONE 02mar16: deploy to local vm with gunicorn, nginx, blah
- recipes to install/deploy in ec2/opsworks
- DONE 02mar16: memcached for prod environment


# 28feb16

## cleanup code

- DONE 28feb16: remove register form and related
- DONE 28feb16: remove db-backed user and related

# 24feb16

## DONE 28feb16: ldap login

- in login, need to authenticate with ldap
- if authenticated, then pull info on groups
- set user obj in cache, login user
- view needs to authorize, according to groups
- for user_loader, needs to pull from cache
- when logout, clear entry from cache
- cache timeout? 24h? force authentication for session older than 24h.
- unit tests!


# 19feb16

- CANCELLED 24feb16: setup ldap test server as fixture -- it might be easier to just mock the ldap server
- REPHRASE 24feb16: tests for ldap login
- WRONG 24feb16: load_user using roles as authorization
- POSTPONED 24feb16: vagrant environ for dev/prod updated


# 16feb16

- DONE 16feb16: functional test for redunlive

## ca_status
- ca_stats.json needs to be protected
- redesign status-board page to get protected ca_stats.json somehow ???
- backend for status-boad:
    * db for cas and their configs
    * ui to edit ca configs in db (add notes, move cas to diff room)
    * flask-admin might help on ui for ca's


# 13feb16

- DONE 13feb16: review cookiecutter to do version, logging
- DONE 13feb16: figure out logging
- DONE 16feb16: shape-up home page
- write tests first
- DONE 16feb16: incorporate redunlive
- POSTPONED 19feb16: this requires design - incorporate ca_status
- CANCELLED 19feb16: users from ldap, not saving into local db - figure an admin view to create users?
- CANCELLED 19feb16: no local users - create the master admin user in manage.py?
  **note**: consider failure to connect to ldap _preventing_ use of cadash
- GO 19feb16: then integrate with ldap
- documentation: add credits to about page



------- 13feb16 deprecated
# 04feb16

- DONE 08feb16: setup database
- learn postgres (using sqlite, for now)


# 03feb16

- admin ui to create users
- integrate auth with ldap
- move rst to md


# 02feb16

- DONE 03feb16: remove create user
- DONE 03feb16: versioning in __init__.py as jay does
  DONE 03feb16: print revision somewhere in the website
- DONE 03feb16: update license to apache2

