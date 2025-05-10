# models/tables.py

from sqlalchemy import Column, String, ForeignKey, DateTime, Uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import datetime

Base = declarative_base()
metadata = Base.metadata

class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    userId = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')

class Message(Base):
    __tablename__ = 'message'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversationId = Column(String(36), ForeignKey('conversation.id'), nullable=False)
    content = Column(String(255), nullable=False)
    userId = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)
    role = Column(String(255), nullable=False)

    conversation = relationship('Conversation', back_populates='messages')

class Roles(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String(255), nullable=False, unique=True)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

    # This will link to Users.roles below
    users = relationship('Users', back_populates='roles', cascade='all, delete-orphan')


class Users(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True) 
    role = Column(String(36), ForeignKey('roles.id'), nullable=False)  # foreign key to roles
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

    # This points back to Roles.users
    roles = relationship('Roles', back_populates='users')
