#!/usr/bin/env python3

# must user varchar[256] for primary key, since straight varchar is not working
# missing documentation for creating a primary key spanning multiple columns
# ERROR: rpc error: code = Unknown desc = max key length exceeded if using varchar[256] for primary key
# missing UNION in select

from immudb.client import ImmudbClient
import crypt, hmac, argparse

class UserManager:
    def __init__(self):
        self.ic=ImmudbClient()
        self.ic.login("immudb", "immudb")

    def init_db(self):
        self.ic.sqlExec("create table if not exists users(username varchar[80], password varchar, active boolean, primary key username)")
        self.ic.sqlExec("create table if not exists groups(groupname varchar[80], username varchar[80], primary key (groupname, username))")
        self.ic.sqlExec("create table if not exists capabilities(capname varchar[80], username varchar[80], groupname varchar[80], primary key (capname, username, groupname))")
        for c in ['reboot','install','uninstall','halt','create_users']:
            self.ic.sqlExec("insert into capabilities(capname, username, groupname) values(@c,'','admin')",{"c":c})
        for c in ['create_data','read_data','update_data','delete_data']:
            self.ic.sqlExec("insert into capabilities(capname, username, groupname) values(@c,'','users')",{"c":c})
            
    def create_admin(self, user, password):
        pw=crypt.crypt(password)
        self.ic.sqlExec("insert into users(username, password, active) values(@user, @password,True)", {"user":user, "password": pw})
        self.ic.sqlExec("insert into groups(groupname, username) values ('admin',@user)",{'user':user})
        self.ic.sqlExec("insert into groups(groupname, username) values ('users',@user)",{'user':user})

    def create_user(self, user, password):
        pw=crypt.crypt(password)
        self.ic.sqlExec("insert into users(username, password, active) values(@user, @password,True)", {"user":user, "password": pw})
        self.ic.sqlExec("insert into groups(groupname, username) values ('users',@user)",{'user':user})

    def override(self, user, capname):
        self.ic.sqlExec("insert into capabilities(capname, username, groupname) values(@capname, @user, '')",{"capname":capname, "user":user})

    def get_cap(self, user):
        res1=self.ic.sqlQuery("select capabilities.capname from users inner join groups on groups.username=users.username inner join capabilities on groups.groupname=capabilities.groupname where users.username=@user",{'user':user})
        res2=self.ic.sqlQuery("select capabilities.capname from capabilities where username=@user",{'user':user})
        return [x[0] for x in res1+res2]
    
    def can_user(self, user, capname):
        return capname in self.get_cap(user)
    
    def user_login(self, username, password):
        t=self.ic.sqlQuery("select password from users where username=@user",{"user": username})
        if len(t)==0:
            return False
        pw=t[0][0]
        return hmac.compare_digest(crypt.crypt(password, pw), pw)
    
if __name__=="__main__":             
    parser = argparse.ArgumentParser(description='User management using immudb')
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    um =UserManager()
    if args.init:
        um.init_db()
        um.create_admin('simone', "nicepassword")
        um.create_user('jeronimo', "blandpassword")
        um.override("simone", "rewind")
        um.override("jeronimo", "reboot")
        
    print("Loggin is as jeronimo with password abc")    
    if um.user_login("jeronimo","abc"):
        print(" succeded")
    else:
        print(" failed")

    print("Loggin is as simone with password nicepassword")    
    if um.user_login("simone","nicepassword"):
        print(" succeded")
    else:
        print(" failed")
        
    print("Simone capabilities:", um.get_cap('simone'))
    print("Can simone create users?", um.can_user('simone','create_users')) 
