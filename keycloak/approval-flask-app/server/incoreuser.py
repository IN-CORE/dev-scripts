
from keycloak import KeycloakAdmin, KeycloakOpenID

server_url = "https://tools.in-core.org/auth/"

class IncoreUserApproval:
    def __init__(self, key_admin):
        self.blacklist = ["@qq.com"]
        self.UNAPPROVED_GROUP_ID = "2434d561-bdf7-4759-b268-f0a0af0d7f02" # for 0unapproved group
        self.INCORE_USER_GROUP_ID = "4fbbb905-4c80-4b69-9b78-00ac7ab55371" # for incore user group
        self.server_url = server_url
        self.key_admin = key_admin
        self.unapproved_users = []
        self.approved_users = []
        self.blacklisted_users = []
        self.get_unapproved_users()
        
    @classmethod
    def init_with_token(cls, token):
        key_admin = cls.get_keycloak_admin_by_token(token)
        return cls(key_admin)
    
    @classmethod
    def init_with_username_password(cls, admin_username, admin_password):
        key_admin = cls.get_keycloak_admin(admin_username, admin_password)
        return cls(key_admin)

    @staticmethod
    def get_keycloak_admin_token(admin_username, admin_password):
        try:
            keycloak_openid = KeycloakOpenID(
                server_url=server_url,
                client_id="admin-cli",
                realm_name="master"
            )
            token = keycloak_openid.token(username=admin_username, password=admin_password, grant_type='password')
            return token
        except Exception as e:
            print(f"Failed to get Keycloak admin token: {e}")
            return None

    @staticmethod
    def get_keycloak_admin_by_token(token):
        try:
            keycloak_admin = KeycloakAdmin(
                server_url=server_url,
                client_id="admin-cli",
                realm_name="In-core",
                token=token
            )
            return keycloak_admin
        except Exception as e:
            print(f"Failed to get Keycloak admin: {e}")
            return None

    @staticmethod
    def get_keycloak_admin(admin_username, admin_password):
        try:
            keycloak_openid = KeycloakOpenID(
                server_url=server_url,
                client_id="admin-cli",
                realm_name="master"
            )
            token = keycloak_openid.token(username=admin_username, password=admin_password, grant_type='password')
            keycloak_admin = KeycloakAdmin(
                server_url=server_url,
                client_id="admin-cli",
                realm_name="In-core",
                token=token
            )
            return keycloak_admin
        except Exception as e:
            print(f"Failed to get Keycloak admin: {e}")
            return None
        
    def get_user_by_id(self, user_id):
        try:
            user = self.key_admin.get_user(user_id)
            return user
        except Exception as e:
            print(f"Failed to get user email: {e}")
            return None
        
    def approve_user_by_id(self, user_id):
        print(f"Approving User {user_id}:")
        try:
            self.key_admin.group_user_add(user_id=user_id, group_id=self.INCORE_USER_GROUP_ID)
            print("\t added to group incore_user")
            self.key_admin.group_user_remove(user_id=user_id, group_id=self.UNAPPROVED_GROUP_ID)
            print("\t removed from group 0unapproved")
            return True
        except Exception as e:
            print(f"Failed to approve user: {e}")
            return False
           
    def approve_user(self, user):
        user_id = user['id']
        print(f"Approving User {user['id']}:")
        if(self.approve_user_by_id(user_id)):
            self.approved_users.append(user)
            return True
        return False

    def approve_users(self, users):
        for user in users:
            if(self.check_blacklist(user['email'])):
                self.blacklisted_users.append(user)
                continue
            self.approve_user(user)

    def get_unapproved_users(self):
        try:
            users = self.key_admin.get_group_members(group_id=self.UNAPPROVED_GROUP_ID)
            if(len(users) == 0):
                print("No unapproved users found")
                return users
            sep = "\t"
            
            # extract subset of dictionary with selected keys
            selected_keys = ['id', 'username', 'email', 'firstName', 'lastName']

            for user in users:
                if(self.check_blacklist(user['email'])):
                    self.blacklisted_users.append({key: user[key] for key in selected_keys if key in user})
                    continue
                self.unapproved_users.append({key: user[key] for key in selected_keys if key in user})
                # print(user['id']+sep+user['username']+sep+user['email']+sep+user['firstName']+sep+user['lastName'])
            return True
        except Exception as e:
            print(f"Failed to get unapproved users: {e}")
            return False
    
    def get_incore_users(self):
        try:
            users = self.key_admin.get_group_members(group_id=self.INCORE_USER_GROUP_ID)
            if(len(users) == 0):
                print("No incore users found")
                return users
           
            # extract subset of dictionary with selected keys
            selected_keys = ['id', 'username', 'email', 'firstName', 'lastName']

            incore_users = []
            for user in users:
                incore_users.append({key: user[key] for key in selected_keys if key in user})
            return incore_users
        except Exception as e:
            print(f"Failed to get incore users: {e}")
            return []

    def summary(self):
        print(f"Unapproved users: {len(self.unapproved_users)}")
        for u in self.unapproved_users:
            print("\t",u)
        print(f"Approved users: {len(self.approved_users)}")
        for u in self.approved_users:
            print("\t",u)
        print(f"Blacklisted users: {len(self.blacklisted_users)}")
        for u in self.blacklisted_users:
            print("\t",u)

    # a function to identify email with their domain name in the blacklist
    def check_blacklist(self, email):
        for domain in self.blacklist:
            if domain in email:
                return True
        return False



