from tortoise import Model, fields
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk = True, index = True)
    username = fields.CharField(max_length = 20, null = False, unique = True)
    nama = fields.CharField(max_length = 50, null = False)
    password = fields.CharField(max_length = 100, null = False)
    alamat = fields.CharField(max_length = 100)
    no_telp = fields.CharField(max_length = 100)
    total_poin = fields.IntField(default = 0)

user_pydantic = pydantic_model_creator(User, name ="User")
user_pydanticIn = pydantic_model_creator(User, name = "UserIn", exclude_readonly = True, exclude = ("total_poin", ))
user_pydanticOut = pydantic_model_creator(User, name = "UserOut", exclude = ("password", ))