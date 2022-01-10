import uuid
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from pydantic import BaseModel, validators
from passlib.context import CryptContext

from . import exceptions
from helpers.config import config


pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


class User(Model):
    __keyspace__ = config['KEYSPACE']
    id = columns.UUID(primary_key=True, default=uuid.uuid1)
    email = columns.Text(primary_key=True, required=True)
    name = columns.Text()
    password = columns.Text()
    is_staff = columns.Boolean(default=False)
    is_verified = columns.Boolean(default=False)
    is_active = columns.Boolean(default=True)
    created_at = columns.DateTime(default=datetime.utcnow)
    updated_at = columns.DateTime(default=datetime.utcnow)
    
    @classmethod
    def get_hash_password(cls, password):
        return pwd_context.hash(password)
    
    def verify_password(self, password):
        # import pdb; pdb.set_trace()
        return pwd_context.verify(password, self.password)
    
    def set_password(self, password):
        self.password = User.get_hash_password(password)
        self.save()
        
    @staticmethod
    def create_user(email, name, password=None):
        q = User.objects.filter(email=email).allow_filtering()
        if q.count() != 0:
            raise exceptions.UserHasAccountException("User already has account.")
        # valid, msg, email = validators._validate_email(email)
        # if not valid:
        #     raise exceptions.InvalidEmailException(f"Invalid email: {msg}")
        obj = User(email=email, name=name)
        obj.password = User.get_hash_password(password)
        obj.save()
        return obj
    
    
class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    
    
class UserLogin(BaseModel):
    email: str
    password: str
    
    
class UserResetPassword(BaseModel):
    email: str
    
    
class ResetPasswordModel(BaseModel):
    uidb64: str
    token: str
    password: str
    
    
    
    
    