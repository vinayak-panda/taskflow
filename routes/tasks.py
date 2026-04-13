from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Task

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')

    query = Task.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify({'success': True, 'tasks': [t.to_dict() for t in tasks], 'count': len(tasks)})


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'success': False, 'error': 'Title is required'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'General'),
        due_date=data.get('due_date'),
        user_id=user_id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()}), 201


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    return jsonify({'success': True, 'task': task.to_dict()})


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    data = request.get_json()
    for field in ['title', 'description', 'status', 'priority', 'category', 'due_date']:
        if field in data:
            setattr(task, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()})


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Task deleted'})


@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    user_id = int(get_jwt_identity())
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify({
        'success': True,
        'stats': {
            'total': len(tasks),
            'todo': sum(1 for t in tasks if t.status == 'todo'),
            'in_progress': sum(1 for t in tasks if t.status == 'in_progress'),
            'done': sum(1 for t in tasks if t.status == 'done'),
            'high': sum(1 for t in tasks if t.priority == 'high'),
            'medium': sum(1 for t in tasks if t.priority == 'medium'),
            'low': sum(1 for t in tasks if t.priority == 'low'),
        }
    })
