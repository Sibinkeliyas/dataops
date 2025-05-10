from db.service.sql.sql_client import SqlClient
from db.service.sql.models.schema import Users, Roles
from sqlalchemy import text
from sqlalchemy.orm import joinedload

class UserManagement (SqlClient):

    def serialize_user(self, user_obj):
        return {
            "id": user_obj.id,
            "name": user_obj.name,
            "email": user_obj.email,
            "createdAt": user_obj.createdAt,
            "updatedAt": user_obj.updatedAt,
            "deletedAt": user_obj.deletedAt,
            "role": {
                "id": user_obj.roles.id,
                "role": user_obj.roles.role
            } if user_obj.roles else None
    }


    async def create_role(self, name):
        session = self.get_session()
        try:
            new_role = Roles(role=name)
            session.add(new_role)
            session.commit()
            session.refresh(new_role)
            return self.to_dict(new_role)
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def get_roles(self):
        session = self.get_session()
        try:
            roles = (session.query(Roles).all())
            print(roles)
            return [self.to_dict(role) for role in roles]
        except Exception as e:
            print(f"Error retrieving roles: {str(e)}")
            return []
        finally:
            session.close()

    def create_user(self, name, email, role_id):
        session = self.get_session()
        try:
            new_user = Users(name=name, email=email, role=role_id)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return self.get_user(email)
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def get_users_list(self) :
        session = self.get_session()
        try:
           users = session.query(Users).options(joinedload(Users.roles)).all()
           print(users)
           return [self.serialize_user(user_obj=user) for user in users]
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return []
        finally:
            session.close()

    def get_user(self, email=None):
        session = self.get_session()
        try:
            user = session.query(Users).filter(Users.email == email).first()
            if user:
                user_dict = {key: value for key, value in user.__dict__.items() if not key.startswith('_')}
                if user.roles:
                    user_dict['role'] = {
                        "id": user.roles.id,
                        "role": user.roles.role
                    }
                return user_dict
            return None
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return None
        finally:
            session.close()

    def delete_user(self, user_id):
        session = self.get_session()
        try:
            user = session.query(Users).filter(Users.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()




