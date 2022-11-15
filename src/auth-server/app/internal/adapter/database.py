import abc
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext import asyncio as asyncio_ext
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Boolean, Column, String, Integer, DateTime, inspect, delete, insert, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, as_declarative
#others
from app.internal.settings import DATABASE_URI, TEST_MODE
#CELERY
from .tasks_celery import process_transactions
#Adapters Interfaces
from .interfaces import RepositoryInterface, RelationalRepositoryInterface, TransactionProcessorInterface
#Entities
from app.internal.domain.entities import Entity

#FOR_TEST_MODE
from .test_database import (test_find, test_find_many, test_find_many_by, test_save, 
    test_update, test_delete, test_delete_many_by)



#___________________________DATABASE__________________________#
SQLALCHEMY_DATABASE_URL='postgresql+asyncpg://'+DATABASE_URI
engine = asyncio_ext.create_async_engine(SQLALCHEMY_DATABASE_URL)

#The future session
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=asyncio_ext.AsyncSession)
#Base = declarative_base()#Used to create database models




#____________________________MODELS______________________________#

@as_declarative()
class Base:
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now())

    def dict(self):
        return {c.key: getattr(self, c.key) 
            for c in inspect(self).mapper.column_attrs}


class UserTable(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    salt = Column(String, default=str(uuid.uuid4))
    username = Column(String)
    password = Column(String)
    is_complete= Column(Boolean, default=False)


class RandomTable(Base):
    __tablename__ = 'randoms'
    id = Column(UUID(as_uuid=True), primary_key=True)
    flow = Column(String, primary_key=True)
    key = Column(String)
    value = Column(String)


class PermissionTable(Base):
    __tablename__ = 'permissions'
    id = Column(String, primary_key=True)
    is_original= Column(Boolean, default=False)


class GroupTable(Base):
    __tablename__ = 'groups'
    id = Column(String, primary_key=True)
    is_original= Column(Boolean, default=False)


class UserPermissionTable(Base):
    __tablename__ = 'user_permissions'
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    permission_id = Column(String, primary_key=True)


class UserGroupTable(Base):
    __tablename__ = 'user_groups'
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    group_id = Column(String, primary_key=True)


class GroupPermissionTable(Base):
    __tablename__ = 'group_permissions'
    group_id = Column(String, primary_key=True)
    permission_id = Column(String, primary_key=True)
    is_original= Column(Boolean, default=False)


class SessionTable(Base):
    __tablename__ = 'sessions'
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    expirated = Column(DateTime)


class LogTable(Base):
    __tablename__ = 'logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    object_type = Column(String)
    object_id = Column(String)
    action = Column(String)
    message = Column(String)



#_________________________CRUD_______________________________#

class AsyncPostgresCRUD(RepositoryInterface):
    model_class=None
    entity_class=None
    tablename=None

    def __init__(self, session:AsyncSession):
        self.session=session

    #you can change this method when extend
    def _get_query(self, unique_data:dict):
        return self.model_class.id == unique_data['id']

    def _format(self, model_object):
        if model_object is None: return None
        if type(model_object) is dict: return self.entity_class(**model_object)
        else: return self.entity_class(**model_object.dict())

    def _format_many(self, model_objects:list):
        entity_objects=[]
        for model_object in model_objects:
            entity_objects.append(self._format(model_object))
        return entity_objects
    
    def get_tablename(self):
        return self.tablename

    async def find(self, unique_data: dict):
        result=None
        if TEST_MODE: result = test_find(self.tablename, unique_data)
        else:
            result = await self.session.execute(select(self.model_class).where(self._get_query(unique_data)))
            result = result.scalars().first()
        return self._format(result)


    async def find_many(self, skip:int=0, limit:int=100):#Alter the order_by
        result=None
        if TEST_MODE: result = test_find_many(self.tablename, skip, limit)
        else:
            query = select(self.model_class).offset(skip).limit(limit).order_by(self.model_class.created)
            result = await self.session.execute(query)
            result = result.scalars().all()
        return self._format_many(result)



class AsyncRelationalPostgresCRUD(AsyncPostgresCRUD, RelationalRepositoryInterface):

    @abc.abstractmethod
    def _get_query_by(self, repeated_data:dict):
        pass

    async def find_many_by(self, repeated_data: dict):
        result=None
        if TEST_MODE: result = test_find_many_by(self.tablename, repeated_data)
        else:
            result = await self.session.execute(select(self.model_class).where(self._get_query_by(repeated_data)))
            result= result.scalars().all()
        return self._format_many(result)


#____________TRANSACTION_PROCESSOR_______________________________#

class TransactionProcessor(TransactionProcessorInterface):
    def __init__(self, db_session):
        self._db_session = db_session
    
    def test_process_transactions(self, transactions_list:list):
        for transaction in transactions_list:
            if transaction.type == 'create': 
                test_save(transaction.tablename, transaction.data)
            elif transaction.type == 'update':
                test_update(transaction.tablename, transaction.id, transaction.data)
            elif transaction.type == 'delete':
                test_delete(transaction.tablename, transaction.id)
            elif transaction.type == 'delete_many_by':
                test_delete_many_by(transaction.tablename, transaction.id)

    async def process(self, transactions_list:list):
        if TEST_MODE: self.test_process_transactions(transactions_list)
        else:
            list_dict = []
            for transaction in transactions_list:
                list_dict.append(transaction.dict())
            process_transactions.delay(list_dict)