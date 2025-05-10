# from services.db.client.BaseClient import BaseClient as Client
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from db.service.sql.models.schema import Message, Conversation, Roles, Users
from db.service.db_client import BaseClient as Client
from sqlalchemy.inspection import inspect
from alembic.config import Config
from alembic import command
import os
from sqlalchemy import asc, desc
import urllib.parse
from alembic.runtime.migration import MigrationContext
from typing import List, Dict, Any
from sqlalchemy import text

class SqlClient(Client):
    def __init__(self, **kwargs):
        self.server_name = kwargs.get('server_name', None)
        self.user_name = kwargs.get('user_name', None)
        self.password = kwargs.get('password', None)
        if self.password and isinstance(self.password,str):
            self.password = self.password.replace('\\','')
        self.db_name = kwargs.get('db_name', None)
        self.port = kwargs.get('port', 3306)
        self.alembic_config = kwargs.get('alembic_config',Config('alembic.ini'))
        self.async_mode = True
        try:
            # encoded_password = urllib.parse.quote_plus(self.password)

            # print(f'mssql+pyodbc://{self.user_name}:{self.password}@{self.server_name}.database.windows.net:{self.port}/{self.db_name}?driver=ODBC+Driver+18+for+SQL+Server')
            self.engine = create_engine('mssql+pyodbc://@sqldataharbor.database.windows.net/sqldbdashboard?driver=ODBC+Driver+18+for+SQL+Server&authentication=ActiveDirectoryDefault')

            self.Session = sessionmaker(bind=self.engine)
            print('Database connection established.')
            # self.run_migrations()
        except Exception as e:
            print(f'Error : {str(e)}')

    def run_migrations(self):
        try:
            # with self.engine.connect() as connection:
            #     context = MigrationContext.configure(connection)
            #     with context.begin_transaction():
            # #         if context.get_current_revision() != context.get_
            # with self.engine.connect() as connection:
            #     context = MigrationContext.configure(connection)
            #     current_revision = context.get_current_revision()
            #     context.
            #     # env_context = EnvironmentContext( self.alembic_config)
            #     # latest_version = env_context.get_head_revision()
            #     # latest_version = command.current(config=self.alembic_config,verbose=True)
            #     # latest_version = get_head_revision()
            #     print(f'Current revision : {current_revision} | target revision : {latest_version}')
            #     if current_revision != latest_version:
            #         print('Running Migrations ...')
            #         command.upgrade(self.alembic_config, "head")
            #         print("Migrations completed !!")
            #         return True
                
            # return False
            print("Generating new migration revision ...")
            command.revision(self.alembic_config, message="Initial migration", autogenerate=True)
            print('Running Migrations ...')
            command.upgrade(self.alembic_config, "head")
            print("Migrations completed !!")
            return True
        except Exception as e:
            print(f'Error : {str(e)}')
            return False

    # def to_dict(self):
    #     return {field.name:getattr(self, field.name) for field in self.__table__.c}

    def to_dict(self,model):
        try:
            as_dict=model.__dict__
            if '_sa_instance_state' in as_dict.keys():
                as_dict.pop('_sa_instance_state')
            return as_dict
        except Exception as e:
            print(f'Error : {str(e)}')
            return model
    def get_session(self):
        return self.Session()

    def ensure(self):
        # Ensure all tables are created
        # Base.metadata.create_all(self.engine)
        pass

    def create_conversation(self, title, user_id):
        session = self.get_session()
        try:
            new_conversation = Conversation(title=title, userId=user_id)
            # print(new_conversation)
            session.add(new_conversation)
            session.commit()
            session.refresh(new_conversation)
            return self.to_dict(new_conversation)
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def delete_conversation(self, conversation_id):
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(Conversation.conversationId == conversation_id).first()
            if conversation:
                session.delete(conversation)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def create_message(self, conversation_id, input_message, user_id, uuid = None):
        session = self.get_session()
        try:
            new_message = Message(conversationId=conversation_id, content=input_message['content'], userId=user_id,role=input_message['role'])
            session.add(new_message)
            session.commit()
            session.refresh(new_message)
            return self.to_dict(new_message)
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def delete_messages(self, message_id):
        session = self.get_session()
        try:
            message = session.query(Message).filter(Message.message_id == message_id).first()
            if message:
                session.delete(message)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f'Error : {str(e)}')
        finally:
            session.close()

    def get_conversation(self, conversation_id, user_id):
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            # return conversation.__dict__
            return conversation.__dict__
        except Exception as e:
            print(f'Error : {str(e)}')
        finally:
            session.close()
    
    def get_conversations(self,user_id, limit = None, sort_order='DESC', offset=0):
        session = self.get_session()
        if sort_order.upper() not in ['ASC','DESC']:
            raise ValueError("Invalid sort_order. Use 'ASC' or 'DESC'.")
        try:
            order_by = desc(Conversation.createdAt) if sort_order.upper() == 'DESC' else asc(Conversation.createdAt)
            conversations = (session.query(Conversation)
                         .filter(Conversation.userId == user_id)
                         .order_by(order_by)
                         .offset(offset)
                         .limit(limit)
                         .all())
            return [self.to_dict(conversation) for conversation in conversations]
        
        except Exception as e:
            print(f"Error retrieving conversations: {str(e)}")
            return []
    
        finally:
            session.close()

    def get_messages(self, conversation_id, user_id, sort_order='ASC'):
        session = self.get_session()
        try:
            order_by = desc(Message.createdAt) if sort_order.upper() == 'DESC' else asc(Message.createdAt)
            messages = (
                session.query(Message)
                .filter(
                    Message.conversationId == conversation_id,
                    Message.userId == user_id
                )
                .order_by(order_by)
                .all()
            )
            return [self.to_dict(message) for message in messages]
        except Exception as e:
            print(f'Error: {str(e)}')
            return []  # Optionally return an empty list or handle the exception as needed
        finally:
            session.close()


    def close(self):
        pass

    def create_group(self):
        # placeholder implementation
        pass

    def get_groups(self):
        pass

    def delete_group(self):
        pass

    async def deactivate_all_workspace_prompts(self, group_id: str, except_prompt_id: str = None) -> None:
        query = text("""
            UPDATE workspace_prompts
            SET active = 0
            WHERE group_id = :group_id AND id != :except_prompt_id
        """)
        await self.session.execute(query, {"group_id": group_id, "except_prompt_id": except_prompt_id})
        await self.session.commit()

    async def get_active_workspace_prompts(self, group_id: str) -> List[Dict[str, Any]]:
        query = text("""
            SELECT * FROM workspace_prompts
            WHERE group_id = :group_id AND active = 1
        """)
        result = await self.session.execute(query, {"group_id": group_id})
        return [dict(row) for row in result]

    async def get_workspace_prompt(self, workspace_prompt_id: str) -> Dict[str, Any]:
        query = text("""
            SELECT * FROM workspace_prompts
            WHERE id = :workspace_prompt_id
        """)
        result = await self.session.execute(query, {"workspace_prompt_id": workspace_prompt_id})
        row = result.fetchone()
        return dict(row) if row else None

    async def update_workspace_prompt(self, workspace_prompt_id: str, **kwargs) -> Dict[str, Any]:
        set_clause = ", ".join(f"{key} = :{key}" for key in kwargs.keys())
        query = text(f"""
            UPDATE workspace_prompts
            SET {set_clause}
            WHERE id = :workspace_prompt_id
            RETURNING *
        """)
        params = {**kwargs, "workspace_prompt_id": workspace_prompt_id}
        result = await self.session.execute(query, params)
        await self.session.commit()
        row = result.fetchone()
        return dict(row) if row else None

    
