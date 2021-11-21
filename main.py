from fastapi import Depends, FastAPI, status, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from models import *
from authentication import *

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {'access_token' : token, 'token_type' : 'bearer'}

@app.post('/registration')
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset = True)
    user_info['password'] = get_password_hash(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)

    return {
        "status" : "ok", 
        "data" : f"Hello {new_user.username} thanks for choosing our services."
    }


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await User.get(id = payload.get("id"))
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await user

@app.get("/users/me/")
async def read_users_me(user: user_pydantic = Depends(get_current_user)):
    return {"data" : user}

@app.get("/profile/{user_id}/")
async def read_profile(user_id: int, user: user_pydantic = Depends(get_current_user)):
    member = await user_pydantic.from_queryset_single(User.get(id=user_id))
    return {
        "status" : "ok",
        "data" : member
    }

@app.put("/profile/{user_id}/")
async def update_profile(user_id : int, userIn: user_pydanticIn, user: user_pydantic = Depends(get_current_user)):
    user_info = userIn.dict(exclude_unset = True)
    user_info['password'] = get_password_hash(user_info['password'])
    await User.filter(id=user_id).update(**user_info)
    return await user_pydantic.from_queryset_single(User.get(id=user_id))

@app.delete("/profile/{user_id}/")
async def delete_profile(user_id: int, user: user_pydantic = Depends(get_current_user)):
    member = await User.get(id = user_id)
    if (member == user):
        member.delete()
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Not authenticated to perform this action",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    return {"status" : "ok"}

host_server = 'sadajiwa-api.postgres.database.azure.com'
db_server_port = '5432'
database_name = 'sadajiwa-api'
db_username = 'sadajiwaadmin@sadajiwa-api'
db_password = 'Sadajiwa123'

DATABASE_URL = 'postgres://{}:{}@{}:{}/{}'.format(db_username, db_password, host_server, db_server_port, database_name)

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={'models': ['models']},
    generate_schemas = True,
    add_exception_handlers = True
)