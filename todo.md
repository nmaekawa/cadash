
# 19feb16

- setup ldap test server as fixture
- tests for ldap login
- load_user using roles as authorization
- vagrant environ for dev/prod updated


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

