from fastapi import FastAPI, Form
from sqlalchemy import create_engine, desc, asc, func
from typing import Annotated

from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED

from json_worker import get_json_data
from models.models import Task, Category, CategoriesTask

app = FastAPI()
db_engine = create_engine('sqlite:///test.db')


@app.post("/task")
async def create_task(task_title: Annotated[str, Form()], task_description: Annotated[str, Form()],
                      categories: Annotated[list, Form()]):
    new_task = Task(task_title=task_title, task_description=task_description)
    with Session(db_engine) as session:
        session.add(new_task)
        session.commit()
        db_categories = [name[0] for name in session.query(Category.category_name).all()]
        for category in categories:
            if category not in db_categories:
                new_category = Category(category_name=category)
                session.add(new_category)
                session.commit()
            else:
                new_category = session.query(Category).filter(Category.category_name == category).one()
            session.add(CategoriesTask(task_id=new_task.id, category_id=new_category.id))
        session.commit()
        session.close()
    return Response(status_code=HTTP_202_ACCEPTED)


@app.get("/tasks/")
async def get_tasks(order: str | None = None, order_field: str | None = None, filter_field: str | None = None,
                    filter_value: str | None = None):
    with (Session(db_engine) as session):
        order_function = desc if order == 'desc' else asc
        order_field = order_field if order_field in ('id', 'task_title', 'task_description', 'created_on') else 'id'
        if filter_field in ('id', 'task_title', 'task_description', 'created_on'):
            tasks = session.query(Task.id, Task.task_description, Task.task_title, Task.created_on,
                                  func.group_concat(Category.category_name, ', ').label('categories')
                                  ).join(CategoriesTask, CategoriesTask.task_id == Task.id, isouter=True
                                         ).join(Category, CategoriesTask.category_id == Category.id, isouter=True
                                                ).filter(getattr(Task, filter_field) == filter_value
                                                         ).order_by(
                order_function(getattr(Task, order_field))).group_by(Task.id)
        else:
            tasks = session.query(Task.id, Task.task_description, Task.task_title, Task.created_on,
                                  func.group_concat(Category.category_name, ', ').label('categories')
                                  ).join(CategoriesTask, CategoriesTask.task_id == Task.id, isouter=True
                                         ).join(Category, CategoriesTask.category_id == Category.id, isouter=True
                                                ).order_by(
                                    order_function(getattr(Task, order_field))).group_by(Task.id)
        session.close()
    return {"tasks": get_json_data(tasks.all(), tasks.statement.columns.keys())}


@app.get("/task/{pk}/")
async def get_task(pk: int):
    with (Session(db_engine) as session):
        task = session.query(Task.id, Task.task_description, Task.task_title, Task.created_on,
                                  func.group_concat(Category.category_name, ', ').label('categories')
                                  ).filter(Task.id == pk
                                           ).join(CategoriesTask, CategoriesTask.task_id == Task.id, isouter=True
                                         ).join(Category, CategoriesTask.category_id == Category.id, isouter=True
                                                ).group_by(Task.id)
    return get_json_data(task.all(), task.statement.columns.keys())


@app.patch("/task/{pk}")
async def change_task(pk: int, task_title: Annotated[str | None, Form()] = None,
                      task_description : Annotated[str | None, Form()] = None):
    with Session(db_engine) as session:
        task = session.query(Task).get(pk)
        if task is None:
            return Response(status_code=HTTP_400_BAD_REQUEST)

        task.task_title = task_title or task.task_title
        task.task_description = task_description or task.task_description
        session.commit()
        session.close()
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.delete("/task/{pk}")
async def delete_task(pk: int):
    with Session(db_engine) as session:
        task = session.query(Task).get(pk)
        if task is None:
            return Response(status_code=HTTP_400_BAD_REQUEST)

        session.delete(task)
        session.commit()
        session.close()
    return Response(status_code=HTTP_204_NO_CONTENT)
