from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, create_engine
from sqlalchemy.orm import declarative_base, backref, relationship

Base = declarative_base()


class Task(Base):
    """Model for Task-object"""
    __tablename__ = 'task'
    id = Column(Integer(), primary_key=True)
    task_title = Column(String(200), nullable=False)
    task_description = Column(Text(), nullable=True)
    created_on = Column(DateTime(), default=datetime.now)


class Category(Base):
    """Model for categories"""
    __tablename__ = 'category'
    id = Column(Integer(), primary_key=True)
    category_name = Column(String(200), nullable=False)


class CategoriesTask(Base):
    """Model for associating categories and tasks"""
    __tablename__ = 'categories_task'
    id = Column(Integer(), primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)


if __name__ == '__main__':
    db = create_engine('sqlite:///../test.db')
    Base.metadata.create_all(db)
