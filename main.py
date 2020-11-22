from typing import List
import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "postgresql://test:test@127.0.0.1:5432/agiliti"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("phone", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.Boolean),
)





class UserEntry(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str
    status: bool


class UserList(BaseModel):
    id: int
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str
    status: bool

class UserUpdate(BaseModel):
    id: int
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str
    status: bool

class UserDelete(BaseModel):
    id: int



app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/users/", response_model=List[UserList])
async def get_user_list():
    query = users.select()
    return await database.fetch_all(query)


@app.post("/users/", response_model=UserList)
async def user_register(user: UserEntry):
    query = users.insert().values(username=user.username, password=user.password,first_name=user.first_name,last_name=user.last_name,phone=user.phone,status=user.status)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.put("/users/", response_model=UserList)
async def update_user(user: UserUpdate):
    query = users.update().where(users.c.id == user.id).values(username=user.username, password=user.password,first_name=user.first_name,last_name=user.last_name,phone=user.phone,status=user.status)
    await database.execute(query)
    return await get_user_by_id(user.id)


@app.get("/users/{user_id}",response_model=UserList)
async def get_user_by_id(userId:int):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)


@app.delete("/users/{user_id}")
async def delete_user(user:UserDelete):
    query = users.delete().where(users.c.id == user.id)
    await database.execute(query)
    return {
        "status":True
    }



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)