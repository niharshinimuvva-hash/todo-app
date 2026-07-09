from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

from pydantic import BaseModel

from uuid import uuid4

from datetime import datetime


class ListSummary(BaseModel):
    id: str
    name: str
    item_count: int

    @staticmethod
    def from_doc(doc):
        return ListSummary(
            id=str(doc["_id"]),
            name=doc["name"],
            item_count=doc["item_count"],
        )


class ToDoListItem(BaseModel):
    id: str
    label: str
    checked: bool

    due_date: str | None = None
    due_time: str | None = None

    status: str = "Pending"

    priority: str = "Medium"

    category: str = "Personal"

    @staticmethod
    def from_doc(item):

        status = item.get("status", "Pending")

        if (
            status != "Completed"
            and item.get("due_date")
            and item.get("due_time")
        ):
            try:
                due = datetime.strptime(
                    f"{item['due_date']} {item['due_time']}",
                    "%Y-%m-%d %H:%M",
                )

                if due < datetime.now():
                    status = "Overdue"

            except:
                pass

        return ToDoListItem(
            id=item["id"],
            label=item["label"],
            checked=item["checked"],
            due_date=item.get("due_date"),
            due_time=item.get("due_time"),
            status=status,
            priority=item.get("priority", "Medium"),
            category=item.get("category", "Personal"),
        )


class ToDoList(BaseModel):
    id: str
    name: str
    items: list[ToDoListItem]

    @staticmethod
    def from_doc(doc):

        items = [
            ToDoListItem.from_doc(item)
            for item in doc["items"]
        ]

        def sort_key(x):
            if x.due_date and x.due_time:
                return f"{x.due_date} {x.due_time}"
            return "9999-12-31 23:59"

        items.sort(key=sort_key)

        return ToDoList(
            id=str(doc["_id"]),
            name=doc["name"],
            items=items,
        )


class ToDoDAL:
    def __init__(self, todo_collection: AsyncIOMotorCollection):
        self._todo_collection = todo_collection

    async def list_todo_lists(
    self,
    user_email: str,
    session=None,
    ):
        async for doc in self._todo_collection.find(
            {
                "user_email": user_email
            },
            projection={
                "name": 1,
                "item_count": {"$size": "$items"},
            },
            sort={"name": 1},
            session=session,
        ):
            yield ListSummary.from_doc(doc)

    async def create_todo_list(
    self,
    name: str,
    user_email: str,
    session=None,
    ):
        response = await self._todo_collection.insert_one(
            {
                "name": name,
                "user_email": user_email,
                "items": [],
            },
            session=session,
        )

        return str(response.inserted_id)

    async def get_todo_list(
    self,
    id,
    user_email,
    session=None,
    ):

        doc = await self._todo_collection.find_one(
            {"_id": ObjectId(id),
            "user_email": user_email,},
            session=session,
        )

        return ToDoList.from_doc(doc)

    async def delete_todo_list(
    self,
    id,
    user_email,
    session=None,
    ):

        response = await self._todo_collection.delete_one(
            {"_id": ObjectId(id),
             "user_email": user_email,},
            session=session,
        )

        return response.deleted_count == 1

    async def create_item(
    self,
    id,
    user_email,
    label,
    due_date=None,
    due_time=None,
    priority="Medium",
    category="Personal",
    session=None,
):

        result = await self._todo_collection.find_one_and_update(
            {
                "_id": ObjectId(id),
                "user_email": user_email,
            },
            {
                "$push": {
    "items": {
        "id": uuid4().hex,
        "label": label,
        "checked": False,
        "due_date": due_date,
        "due_time": due_time,
        "status": "Pending",
        "priority": priority,
        "category": category,
    }
}
            },
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if result:
            return ToDoList.from_doc(result)

    async def set_checked_state(
        self,
        doc_id,
        user_email,
        item_id,
        checked_state,
        session=None,
    ):

        update = {
    "items.$.checked": checked_state,
    "items.$.status": "Completed" if checked_state else "Pending",
}

        result = await self._todo_collection.find_one_and_update(
            {
                "_id": ObjectId(doc_id),
                "user_email": user_email,
                "items.id": item_id,
            },
            {
                "$set": update
            },
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if result:
            return ToDoList.from_doc(result)
    async def update_item(
        self,
        doc_id,
        user_email,
        item_id,
        label,
        due_date,
        due_time,
        priority,
        category,
        session=None,
    ):

        result = await self._todo_collection.find_one_and_update(
            {
                "_id": ObjectId(doc_id),
                "user_email": user_email,
                "items.id": item_id,
            },
            {
                "$set": {
                    "items.$.label": label,
                    "items.$.due_date": due_date,
                    "items.$.due_time": due_time,
                    "items.$.priority": priority,
                    "items.$.category": category,
                }
            },
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if result:
            return ToDoList.from_doc(result)

    async def delete_item(
        self,
        doc_id,
        user_email,
        item_id,
        session=None,
    ):

        result = await self._todo_collection.find_one_and_update(
            {
                "_id": ObjectId(doc_id),
                "user_email": user_email,
            },
            {
                "$pull": {
                    "items": {
                        "id": item_id
                    }
                }
            },
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if result:
            return ToDoList.from_doc(result)