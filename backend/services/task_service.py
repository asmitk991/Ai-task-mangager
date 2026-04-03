from typing import Iterable, List

from sqlalchemy.orm import Session

from models.task import Task
from schemas.task import CreateTaskRequest, UpdateTaskRequest
from utils.exceptions import NotFoundError


def list_tasks(db: Session) -> List[Task]:
    return db.query(Task).order_by(Task.created_at.desc(), Task.id.desc()).all()


def create_tasks(db: Session, tasks: Iterable[CreateTaskRequest]) -> List[Task]:
    db_tasks = []
    for task in tasks:
        db_task = Task(
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            priority=task.priority,
            category=task.category,
            status=task.status,
            raw_input=task.raw_input,
        )
        db.add(db_task)
        db_tasks.append(db_task)

    db.commit()

    for task in db_tasks:
        db.refresh(task)

    return db_tasks


def update_task(db: Session, task_id: int, payload: UpdateTaskRequest) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundError(f"Task with id {task_id} was not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> None:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundError(f"Task with id {task_id} was not found.")

    db.delete(task)
    db.commit()
