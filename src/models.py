"""
Database models for the web application.

This module defines SQLAlchemy ORM models for the application's data layer.
It includes models for tasks, categories, and user-related data.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class User(db.Model):
    """
    User model for authentication and user-specific data.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        password_hash (str): Hashed password
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last update timestamp
        is_active (bool): Whether the account is active
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """
        Convert user object to dictionary representation.
        
        Returns:
            Dictionary with user data (excluding password)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f'<User {self.username}>'


class Category(db.Model):
    """
    Category model for organizing tasks.
    
    Attributes:
        id (int): Primary key
        name (str): Category name
        description (str): Optional description
        color (str): Hex color code for visual identification
        user_id (int): Foreign key to User
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    color = db.Column(db.String(7), default='#007bff', nullable=False)  # Hex color code
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """
        Convert category object to dictionary representation.
        
        Returns:
            Dictionary with category data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation of the Category model."""
        return f'<Category {self.name}>'


class Task(db.Model):
    """
    Task model for managing to-do items.
    
    Attributes:
        id (int): Primary key
        title (str): Task title
        description (str): Detailed description
        status (str): Current status (pending, in_progress, completed)
        priority (int): Priority level (1-5, where 1 is highest)
        due_date (datetime): Optional due date
        completed_at (datetime): When the task was completed
        user_id (int): Foreign key to User
        category_id (int): Foreign key to Category
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'tasks'
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    
    VALID_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED]
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    priority = db.Column(db.Integer, default=3, nullable=False)  # 1-5 scale
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        """
        Initialize Task with validation.
        
        Args:
            **kwargs: Task attributes
            
        Raises:
            ValueError: If invalid status or priority provided
        """
        super(Task, self).__init__(**kwargs)
        
        # Validate status
        if 'status' in kwargs and kwargs['status'] not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
        
        # Validate priority
        if 'priority' in kwargs and (kwargs['priority'] < 1 or kwargs['priority'] > 5):
            raise ValueError("Priority must be between 1 and 5")
    
    def mark_completed(self) -> None:
        """Mark task as completed and set completion timestamp."""
        self.status = self.STATUS_COMPLETED
        self.completed_at = datetime.utcnow()
    
    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = self.STATUS_IN_PROGRESS
        self.completed_at = None
    
    def mark_pending(self) -> None:
        """Mark task as pending."""
        self.status = self.STATUS_PENDING
        self.completed_at = None
    
    def is_overdue(self) -> bool:
        """
        Check if the task is overdue.
        
        Returns:
            True if task has a due date in the past and is not completed
        """
        if self.due_date and self.status != self.STATUS_COMPLETED:
            return datetime.utcnow() > self.due_date
        return False
    
    def to_dict(self) -> dict:
        """
        Convert task object to dictionary representation.
        
        Returns:
            Dictionary with task data
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self) -> str:
        """String representation of the Task model."""
        return f'<Task {self.title} [{self.status}]>'


class TaskAttachment(db.Model):
    """
    Model for file attachments on tasks.
    
    Attributes:
        id (int): Primary key
        filename (str): Original filename
        filepath (str): Path to stored file
        file_size (int): File size in bytes
        mime_type (str): MIME type of the file
        task_id (int): Foreign key to Task
        uploaded_by (int): Foreign key to User who uploaded
        created_at (datetime): Upload timestamp
    """
    
    __tablename__ = 'task_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = db.relationship('Task', backref=db.backref('attachments', lazy='dynamic', cascade='all, delete-orphan'))
    uploader = db.relationship('User', backref=db.backref('uploaded_attachments', lazy='dynamic'))
    
    def to_dict(self) -> dict:
        """
        Convert attachment object to dictionary representation.
        
        Returns:
            Dictionary with attachment data
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'task_id': self.task_id,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation of the TaskAttachment model."""
        return f'<TaskAttachment {self.filename}>'


class TaskComment(db.Model):
    """
    Model for comments on tasks.
    
    Attributes:
        id (int): Primary key
        content (str): Comment text
        task_id (int): Foreign key to Task
        user_id (int): Foreign key to User
        created_at (datetime): Comment creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'task_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = db.relationship('Task', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan'))
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    
    def to_dict(self) -> dict:
        """
        Convert comment object to dictionary representation.
        
        Returns:
            Dictionary with comment data
        """
        return {
            'id': self.id,
            'content': self.content,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'author_username': self.author.username if self.author else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation of the TaskComment model."""
        return f'<TaskComment by {self.author.username if self.author else "Unknown"}>'


def init_db(app):
    """
    Initialize the database with the Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        SQLAlchemy instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default categories if they don't exist
        _create_default_categories()
    
    return db


def _create_default_categories():
    """
    Create default categories for new users.
    This function is called during database initialization.
    """
    from flask import current_app
    
    # Default categories that can be assigned to users
    default_categories = [
        {'name': 'Work', 'description': 'Work-related tasks', 'color': '#007bff'},
        {'name': 'Personal', 'description': 'Personal tasks and errands', 'color': '#28a745'},
        {'name': 'Urgent', 'description': 'High priority tasks', 'color': '#dc3545'},
        {'name': 'Ideas', 'description': 'Ideas and brainstorming', 'color': '#ffc107'},
        {'name': 'Learning', 'description': 'Learning and development', 'color': '#17a2b8'}
    ]
    
    # Note: Default categories are created per user in the user registration process
    # This function serves as a template for category creation
    pass


def reset_database(app):
    """
    Drop and recreate all database tables.
    WARNING: This will delete all data!
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        _create_default_categories()