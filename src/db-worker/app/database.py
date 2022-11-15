import abc
import uuid
from datetime import datetime
from sqlalchemy import (create_engine, delete, inspect,
    Boolean, Column, ForeignKey, Integer, String, DateTime)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base, as_declarative
#others
from app.settings import DATABASE_URI
from pydantic import ValidationError


#_______________________DATABASE_________________________________________#
SQLALCHEMY_DATABASE_URL='postgresql://'+DATABASE_URI
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#The future session
SessionLocal = sessionmaker(autocommit=False, expire_on_commit=True, autoflush=True, bind=engine)
#Base = declarative_base()#Used to create database models


#____________________________MODELS______________________________#

@as_declarative()
class Base:
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now())

    def _asdict(self):
        return {c.key: getattr(self, c.key) 
            for c in inspect(self).mapper.column_attrs}

#ONLY FOR DB-WORKER
class StatusTable(Base):
    __tablename__='status'
    id = Column(String, primary_key=True)
    value = Column(String)


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



#_____________________________________CRUD_______________________________#
class BaseEDIT():

    model_class=None
    validator_create_class=None
    validator_update_class=None
    _errors=None

    def __init__(self, db:Session):
        self.db=db

    def _get_query(self, unique_data_dict:dict):
        return self.model_class.id == unique_data_dict['id']

    def create_object(self, object_schema:dict):
        db_object = self.model_class(**object_schema)
        self.db.add(db_object)

    def update_object(self, unique_data_dict:dict, new_data_schema:dict):
        self.db.query(self.model_class).filter(self._get_query(unique_data_dict)).update(new_data_schema)

    def delete_object(self, unique_data_dict:dict):
        query = delete(self.model_class).where(self._get_query(unique_data_dict))
        self.db.execute(query)

    def validate_create(self, data_dict:dict):
        if self.validator_create_class is None: return False
        try: self.validator_create_class.validate(data_dict)
        except ValidationError as ex:
            self._errors = [ex.json()]
            return False
        return True

    def validate_update(self, data_dict:dict):
        if self.validator_update_class is None: return False
        try: self.validator_update_class.validate(data_dict)
        except ValidationError as ex:
            self._errors = [ex.json()]
            return False
        return True

    def get_errors(self):
        if self._errors is None:
            return ['validator not declared']
        return self._errors

class BaseRelationalEDIT(BaseEDIT, abc.ABC):
    @abc.abstractmethod
    def _get_query_by(self, repeated_data_dict:dict):
        pass
    
    def delete_many_objects_by(self, repeated_data_dict:dict):
        query = delete(self.model_class).where(self._get_query_by(repeated_data_dict))
        self.db.execute(query)
