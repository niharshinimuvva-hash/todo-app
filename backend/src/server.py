from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys

from bson import ObjectId
from fastapi import FastAPI, status, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import uvicorn

from dal import ToDoDAL, ListSummary, ToDoList
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

from auth_models import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)

COLLECTION_NAME = "todo_lists"
USER_COLLECTION = "users"
MONGODB_URI = os.environ["MONGODB_URI"]
DEBUG = os.environ.get("DEBUG", "").strip().lower() in {
    "1",
    "true",
    "on",
    "yes",
}


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = AsyncIOMotorClient(MONGODB_URI)
    database = client.get_default_database()

    pong = await database.command("ping")

    if int(pong["ok"]) != 1:
        raise Exception("Cluster connection is not okay!")

    todo_lists = database.get_collection(COLLECTION_NAME)
    users = database.get_collection(USER_COLLECTION)

    app.todo_dal = ToDoDAL(todo_lists)
    app.users = users

    yield

    client.close()


app = FastAPI(
    lifespan=lifespan,
    debug=DEBUG,
)

# ----------------------------------------------------
# AUTHENTICATION
# ----------------------------------------------------

@app.post("/api/register")
async def register(user: RegisterRequest):

    existing = await app.users.find_one(
        {"email": user.email}
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    result = await app.users.insert_one(
        {
            "username": user.username,
            "email": user.email,
            "password": hash_password(user.password),
        }
    )

    return UserResponse(
        id=str(result.inserted_id),
        username=user.username,
        email=user.email,
    )


@app.post("/api/login")
async def login(
    credentials: LoginRequest,
) -> TokenResponse:

    user = await app.users.find_one(
        {"email": credentials.email}
    )

    if (
        user is None
        or not verify_password(
            credentials.password,
            user["password"],
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {
            "sub": user["email"],
        }
    )

    return TokenResponse(
        access_token=token
    )


@app.get("/api/me")
async def get_me(
    email: str = Depends(get_current_user),
):

    user = await app.users.find_one(
        {"email": email}
    )

    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
    )
# ----------------------------------------------------
# LISTS
# ----------------------------------------------------

@app.get("/api/lists")
async def get_all_lists(
    email: str = Depends(get_current_user),
) -> list[ListSummary]:

    return [
        i async for i in app.todo_dal.list_todo_lists(email)
    ]


class NewList(BaseModel):
    name: str


class NewListResponse(BaseModel):
    id: str
    name: str


@app.post(
    "/api/lists",
    status_code=status.HTTP_201_CREATED,
)
async def create_todo_list(
    new_list: NewList,
    email: str = Depends(get_current_user),
) -> NewListResponse:

    return NewListResponse(
        id=await app.todo_dal.create_todo_list(
            new_list.name,
            email,
        ),
        name=new_list.name,
    )


@app.get("/api/lists/{list_id}")
async def get_list(
    list_id: str,
    email: str = Depends(get_current_user),
) -> ToDoList:

    return await app.todo_dal.get_todo_list(
        list_id,
        email,
    )


@app.delete("/api/lists/{list_id}")
async def delete_list(
    list_id: str,
    email: str = Depends(get_current_user),
):

    return await app.todo_dal.delete_todo_list(
        list_id,
        email,
    )


# ----------------------------------------------------
# ITEMS
# ----------------------------------------------------

class NewItem(BaseModel):

    label: str

    due_date: str | None = None

    due_time: str | None = None

    priority: str = "Medium"

    category: str = "Personal"


@app.post(
    "/api/lists/{list_id}/items/",
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    list_id: str,
    new_item: NewItem,
    email: str = Depends(get_current_user),
) -> ToDoList:

    return await app.todo_dal.create_item(
        list_id,
        email,
        label=new_item.label,
        due_date=new_item.due_date,
        due_time=new_item.due_time,
        priority=new_item.priority,
        category=new_item.category,
    )


@app.delete("/api/lists/{list_id}/items/{item_id}")
async def delete_item(
    list_id: str,
    item_id: str,
    email: str = Depends(get_current_user),
) -> ToDoList:

    return await app.todo_dal.delete_item(
        list_id,
        email,
        item_id,
    )


class ToDoItemUpdate(BaseModel):

    item_id: str

    checked_state: bool
class EditItem(BaseModel):
    label: str
    due_date: str | None = None
    due_time: str | None = None
    priority: str = "Medium"
    category: str = "Personal"

@app.patch("/api/lists/{list_id}/checked_state")
async def set_checked_state(
    list_id: str,
    update: ToDoItemUpdate,
    email: str = Depends(get_current_user),
) -> ToDoList:
    
    
    return await app.todo_dal.set_checked_state(
        list_id,
        email,
        update.item_id,
        update.checked_state,
    )

@app.patch("/api/lists/{list_id}/items/{item_id}")
async def edit_item(
    list_id: str,
    item_id: str,
    item: EditItem,
    email: str = Depends(get_current_user),
):

    return await app.todo_dal.update_item(
        list_id,
        email,
        item_id,
        item.label,
        item.due_date,
        item.due_time,
        item.priority,
        item.category,
    )
# ----------------------------------------------------
# DUMMY ROUTE
# ----------------------------------------------------

class DummyResponse(BaseModel):
    id: str
    when: datetime


@app.get("/api/dummy")
async def get_dummy():

    return DummyResponse(
        id=str(ObjectId()),
        when=datetime.now(),
    )


def main(argv=sys.argv[1:]):
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=3001,
            reload=DEBUG,
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()