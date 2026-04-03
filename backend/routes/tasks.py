from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest

from database.db import SessionLocal
from schemas.task import (
    CreateTaskRequest,
    CreateTasksBatchRequest,
    ParseTaskRequest,
    ParseTaskResponse,
    TaskResponse,
    TasksResponse,
    UpdateTaskRequest,
)
from services.gemini_service import GeminiTaskParser
from services.task_service import create_tasks, delete_task, list_tasks, update_task
from utils.exceptions import GeminiAPIError, GeminiResponseError, NotFoundError


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/parse-task", methods=["POST"])
def parse_task():
    try:
        payload = ParseTaskRequest.model_validate(request.get_json(force=True, silent=False) or {})
        parser = GeminiTaskParser()
        parsed_tasks = parser.parse_tasks(payload.text)
        response = ParseTaskResponse(tasks=parsed_tasks)
        return jsonify(response.model_dump(mode="json")), 200
    except BadRequest as exc:
        return jsonify({"error": "Invalid JSON", "details": str(exc)}), 400
    except ValidationError as exc:
        return jsonify({"error": "Validation error", "details": exc.errors()}), 400
    except (GeminiAPIError, GeminiResponseError) as exc:
        return jsonify({"error": "AI parsing failed", "details": str(exc)}), 502
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "Unexpected server error", "details": str(exc)}), 500


@tasks_bp.post("/tasks")
def create_tasks_route():
    db = SessionLocal()
    try:
        data = request.get_json(force=True, silent=False) or {}

        if "tasks" in data:
            payload = CreateTasksBatchRequest.model_validate(data)
            created = create_tasks(db, payload.tasks)
        else:
            single_task = CreateTaskRequest.model_validate(data)
            created = create_tasks(db, [single_task])

        response = TasksResponse(tasks=[TaskResponse.model_validate(task) for task in created])
        return jsonify(response.model_dump(mode="json")), 201
    except BadRequest as exc:
        return jsonify({"error": "Invalid JSON", "details": str(exc)}), 400
    except ValidationError as exc:
        return jsonify({"error": "Validation error", "details": exc.errors()}), 400
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return jsonify({"error": "Unexpected server error", "details": str(exc)}), 500
    finally:
        db.close()


@tasks_bp.get("/tasks")
def get_tasks_route():
    db = SessionLocal()
    try:
        tasks = list_tasks(db)
        response = TasksResponse(tasks=[TaskResponse.model_validate(task) for task in tasks])
        return jsonify(response.model_dump(mode="json")), 200
    finally:
        db.close()


@tasks_bp.put("/tasks/<int:task_id>")
def update_task_route(task_id: int):
    db = SessionLocal()
    try:
        payload = UpdateTaskRequest.model_validate(request.get_json(force=True, silent=False) or {})
        task = update_task(db, task_id, payload)
        return jsonify(TaskResponse.model_validate(task).model_dump(mode="json")), 200
    except BadRequest as exc:
        return jsonify({"error": "Invalid JSON", "details": str(exc)}), 400
    except ValidationError as exc:
        return jsonify({"error": "Validation error", "details": exc.errors()}), 400
    except NotFoundError as exc:
        return jsonify({"error": "Not found", "details": str(exc)}), 404
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return jsonify({"error": "Unexpected server error", "details": str(exc)}), 500
    finally:
        db.close()


@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task_route(task_id: int):
    db = SessionLocal()
    try:
        delete_task(db, task_id)
        return jsonify({"message": f"Task {task_id} deleted successfully."}), 200
    except NotFoundError as exc:
        return jsonify({"error": "Not found", "details": str(exc)}), 404
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return jsonify({"error": "Unexpected server error", "details": str(exc)}), 500
    finally:
        db.close()
