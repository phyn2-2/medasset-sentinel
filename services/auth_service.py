"""
MedAsset Sentinel - Authentication Service
Handles admin login, logout and session management
"""
from models import Admin
from extensions import db

class AuthService:
    """Authentication business logic"""

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate admin user with username and password
        Args:
            username (str): Admin username
            password (str): Plain text password
        Returns:
            Admin: Admin object if Authentication successful
            None: if Authentication fails
        """
        if not username or not password:
            return None

        # Query admin by username
        admin = Admin.query.filter_by(username=username).first()

        if admin is None:
            return None

        # Check if admin is active
        if not admin.is_active:
            return None

        # Verify password
        if not admin.check_password(password):
            return None

        return admin

    @staticmethod
    def get_admin_by_id(admin_id):
        """
        Retrieve admin by ID (for session management)
        Args:
            admin_id (int): Admin ID
        Returns:
            Admin: Admin object or None
        """
        return Admin.query.get(int(admin_id))

    @staticmethod
    def create_admin(username, password):
        """
        Create new admin user (future: admin management)
        Args:
            username (str): Unique username
            password (str): Plain text password (will be hashed)
        Returns:
            tuple: (Admin object, error_message)
        """
        # Validate input
        if not username or len(username) < 3:
            return None, "Username must be at least 3 characters"

        if not password or len(password) < 8:
            return None, "Password must be at least 8 characters"

        # Check if username already exists
        existing = Admin.query.filter_by(username=username).first()
        if existing:
            return None, "Username already exists"

        # Create admin
        admin = Admin(username=username)
        admin.set_password(password)

        try:
            db.session.add(admin)
            db.session.commit()
            return admin, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"

    @staticmethod
    def deactivate_admin(admin_id):
        """
        Deactivate admin account (soft delete)
        Args:
            admin_id (int): Admin ID
        Returns:
            bool: True if successful, False otherwise
        """
        admin = Admin.query.get(admin_id)

        if not admin:
            return False

        admin.is_active = False

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False



