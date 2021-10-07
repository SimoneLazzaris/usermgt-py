# usermgt-py
User management and permission with immudb backend

# Scope

This is a simple (toy) library that handles user authentication and authorization, with immudb as backend

# Usage

At the moment, this library is not properly initialized, so you just have to include the `usermgt.py` file in your project.
It adds a class (`UserManager`) that you can use. Note that it will use default credentials to access immudb, which is supposed to be found at the default location.

## Methods

* `create_user`: Create a user with standard capabilities
* `create_admin`: Create a user with admin capabilities
* `override`: Add a single capability to a user
* `get_cap`: Get capability list for a user
* `can_user`: Checks if a user has a certain capability
* `user_login`: Check username and password against the database

# Friction points:
* I had to use varchar[nn] for primary key, since straight varchar is not working; older version were different (?)
* Missing documentation for creating a primary key spanning multiple columns
* `ERROR: rpc error: code = Unknown desc = max key length exceeded` if using varchar[256] for primary key. I had to reduce the length of the field.
* [minor] missing UNION in select
