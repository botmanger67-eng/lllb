"""
Main application entry point for the Task Efficiency Demonstrator web application.
This module initializes the Flask application, configures the database,
and defines all route handlers.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    jsonify,
    abort
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///tasks.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize database
db = SQLAlchemy(app)


class Task(db.Model):
    """
    Task model representing a task to be accomplished.
    
    Attributes:
        id (int): Primary key
        title (str): Task title
        description (str): Detailed description of the task
        category (str): Task category (e.g., 'development', 'design', 'testing')
        priority (int): Priority level (1-5, where 5 is highest)
        status (str): Current status ('pending', 'in_progress', 'completed', 'cancelled')
        created_at (datetime): Timestamp when task was created
        updated_at (datetime): Timestamp when task was last updated
        completed_at (datetime): Timestamp when task was completed
    """
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')
    priority = db.Column(db.Integer, nullable=False, default=3)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task instance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        """String representation of the Task instance."""
        return f'<Task {self.id}: {self.title}>'


# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


# Error handlers
@app.errorhandler(404)
def not_found_error(error: HTTPException) -> tuple:
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error: HTTPException) -> tuple:
    """Handle 500 errors."""
    db.session.rollback()
    logger.error(f"500 error: {error}")
    return render_template('errors/500.html'), 500


@app.errorhandler(400)
def bad_request_error(error: HTTPException) -> tuple:
    """Handle 400 errors."""
    logger.warning(f"400 error: {error}")
    return render_template('errors/400.html'), 400


# Route handlers
@app.route('/')
def index() -> str:
    """
    Home page route.
    
    Returns:
        str: Rendered HTML template for the home page
    """
    try:
        # Get task statistics
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        in_progress_tasks = Task.query.filter_by(status='in_progress').count()
        
        # Get recent tasks
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        
        return render_template(
            'index.html',
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            recent_tasks=recent_tasks
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in index route: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('index.html', total_tasks=0, completed_tasks=0,
                             pending_tasks=0, in_progress_tasks=0, recent_tasks=[])


@app.route('/tasks')
def list_tasks() -> str:
    """
    List all tasks with optional filtering.
    
    Query Parameters:
        category (str): Filter by category
        status (str): Filter by status
        priority (int): Filter by priority
        
    Returns:
        str: Rendered HTML template with task list
    """
    try:
        # Build query with optional filters
        query = Task.query
        
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        priority = request.args.get('priority', type=int)
        if priority:
            query = query.filter_by(priority=priority)
        
        # Order by priority (highest first) then by creation date
        tasks = query.order_by(Task.priority.desc(), Task.created_at.desc()).all()
        
        # Get unique categories for filter dropdown
        categories = db.session.query(Task.category).distinct().all()
        categories = [c[0] for c in categories]
        
        return render_template(
            'tasks/list.html',
            tasks=tasks,
            categories=categories,
            current_filters={'category': category, 'status': status, 'priority': priority}
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_tasks route: {e}")
        flash('An error occurred while loading tasks.', 'error')
        return render_template('tasks/list.html', tasks=[], categories=[], current_filters={})


@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task() -> str:
    """
    Create a new task.
    
    GET: Display the creation form
    POST: Process the form submission and create the task
    
    Returns:
        str: Rendered HTML template or redirect
    """
    if request.method == 'POST':
        try:
            # Validate required fields
            title = request.form.get('title', '').strip()
            if not title:
                flash('Title is required.', 'error')
                return render_template('tasks/create.html')
            
            # Create new task
            task = Task(
                title=title,
                description=request.form.get('description', '').strip(),
                category=request.form.get('category', 'general').strip(),
                priority=int(request.form.get('priority', 3)),
                status=request.form.get('status', 'pending')
            )
            
            db.session.add(task)
            db.session.commit()
            
            logger.info(f"Task created successfully: {task.id}")
            flash('Task created successfully!', 'success')
            return redirect(url_for('view_task', task_id=task.id))
            
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            logger.error(f"Error creating task: {e}")
            flash('An error occurred while creating the task.', 'error')
            return render_template('tasks/create.html')
    
    return render_template('tasks/create.html')


@app.route('/tasks/<int:task_id>')
def view_task(task_id: int) -> str:
    """
    View a specific task.
    
    Args:
        task_id (int): The ID of the task to view
        
    Returns:
        str: Rendered HTML template with task details
    """
    try:
        task = Task.query.get_or_404(task_id)
        return render_template('tasks/view.html', task=task)
    except SQLAlchemyError as e:
        logger.error(f"Database error in view_task route: {e}")
        abort(500)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id: int) -> str:
    """
    Edit an existing task.
    
    GET: Display the edit form
    POST: Process the form submission and update the task
    
    Args:
        task_id (int): The ID of the task to edit
        
    Returns:
        str: Rendered HTML template or redirect
    """
    try:
        task = Task.query.get_or_404(task_id)
        
        if request.method == 'POST':
            # Validate required fields
            title = request.form.get('title', '').strip()
            if not title:
                flash('Title is required.', 'error')
                return render_template('tasks/edit.html', task=task)
            
            # Update task fields
            task.title = title
            task.description = request.form.get('description', '').strip()
            task.category = request.form.get('category', 'general').strip()
            task.priority = int(request.form.get('priority', 3))
            
            new_status = request.form.get('status', 'pending')
            if new_status != task.status:
                task.status = new_status
                if new_status == 'completed':
                    task.completed_at = datetime.utcnow()
                elif task.completed_at:
                    task.completed_at = None
            
            db.session.commit()
            
            logger.info(f"Task updated successfully: {task.id}")
            flash('Task updated successfully!', 'success')
            return redirect(url_for('view_task', task_id=task.id))
        
        return render_template('tasks/edit.html', task=task)
        
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        logger.error(f"Error updating task {task_id}: {e}")
        flash('An error occurred while updating the task.', 'error')
        return render_template('tasks/edit.html', task=task)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id: int) -> str:
    """
    Delete a task.
    
    Args:
        task_id (int): The ID of the task to delete
        
    Returns:
        str: Redirect to task list
    """
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Task deleted successfully: {task_id}")
        flash('Task deleted successfully!', 'success')
        return redirect(url_for('list_tasks'))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting task {task_id}: {e}")
        flash('An error occurred while deleting the task.', 'error')
        return redirect(url_for('list_tasks'))


@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        task_id (int): The ID of the task to complete
        
    Returns:
        str: Redirect to task view
    """
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Task completed: {task_id}")
        flash('Task marked as completed!', 'success')
        return redirect(url_for('view_task', task_id=task.id))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error completing task {task_id}: {e}")
        flash('An error occurred while completing the task.', 'error')
        return redirect(url_for('view_task', task_id=task_id))


# API routes for programmatic access
@app.route('/api/tasks', methods=['GET'])
def api_list_tasks() -> tuple:
    """
    API endpoint to list all tasks.
    
    Returns:
        tuple: JSON response with task list and status code
    """
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200
    except SQLAlchemyError as e:
        logger.error(f"API error listing tasks: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def api_get_task(task_id: int) -> tuple:
    """
    API endpoint to get a specific task.
    
    Args:
        task_id (int): The ID of the task
        
    Returns:
        tuple: JSON response with task data and status code
    """
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200
    except SQLAlchemyError as e:
        logger.error(f"API error getting task {task_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks', methods=['POST'])
def api_create_task() -> tuple:
    """
    API endpoint to create a new task.
    
    Expects JSON body with task data.
    
    Returns:
        tuple: JSON response with created task and status code
    """
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            priority=data.get('priority', 3),
            status=data.get('status', 'pending')
        )
        
        db.session.add(task)
        db.session.commit()
        
        logger.info(f"API task created: {task.id}")
        return jsonify(task.to_dict()), 201
        
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        logger.error(f"API error creating task: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Health check endpoint
@app.route('/health')
def health_check() -> tuple:
    """
    Health check endpoint for monitoring.
    
    Returns:
        tuple: JSON response with health status
    """
    try:
        # Check database connectivity
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except SQLAlchemyError:
        db_status = 'unhealthy'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if db_status == 'healthy' else 503


if __name__ == '__main__':
    """
    Run the application when executed directly.
    """
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Task Efficiency Demonstrator on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )