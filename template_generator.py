#!/usr/bin/env python3
"""
SaaS Template Generator
Command-line tool to customize the SaaS template for different use cases
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any
import argparse

from template_config import (
    SaaSTemplate, 
    create_rent_tracking_config,
    create_subscription_saas_config,
    create_project_management_config
)

class TemplateGenerator:
    """Generates and customizes SaaS templates"""
    
    def __init__(self, template_config: SaaSTemplate):
        self.config = template_config
        self.template_dir = Path(__file__).parent
        self.output_dir = None
    
    def generate(self, output_dir: str, overwrite: bool = False):
        """Generate a customized SaaS application"""
        self.output_dir = Path(output_dir)
        
        if self.output_dir.exists() and not overwrite:
            print(f"Output directory {output_dir} already exists. Use --overwrite to replace it.")
            return False
        
        if self.output_dir.exists() and overwrite:
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating SaaS template: {self.config.branding.app_name}")
        print(f"Output directory: {output_dir}")
        
        # Copy base template files
        self._copy_base_files()
        
        # Generate customized configuration
        self._generate_config_files()
        
        # Update branding and content
        self._update_branding()
        
        # Generate database schema
        self._generate_database_schema()
        
        # Generate feature modules
        self._generate_feature_modules()
        
        # Generate frontend components
        self._generate_frontend()
        
        # Generate documentation
        self._generate_documentation()
        
        print(f"✅ Template generated successfully!")
        print(f"📁 Location: {self.output_dir.absolute()}")
        print(f"🚀 Next steps:")
        print(f"   cd {output_dir}")
        print(f"   python -m venv venv")
        print(f"   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print(f"   pip install -r backend/requirements.txt")
        print(f"   cd backend && python database_init.py")
        print(f"   python app.py")
        
        return True
    
    def _copy_base_files(self):
        """Copy base template files to output directory"""
        print("📂 Copying base template files...")
        
        # Define files/directories to copy (excluding rent-specific ones)
        base_files = [
            'backend/app.py',
            'backend/config.py',
            'backend/database.py',
            'backend/database_sqlite.py',
            'backend/models/user.py',
            'backend/models/__init__.py',
            'backend/routes/auth.py',
            'backend/routes/__init__.py',
            'backend/utils/email_service.py',
            'backend/utils/notification_service.py',
            'backend/utils/__init__.py',
            'backend/requirements.txt',
            'frontend/styles.css',
            'frontend/app.js'
        ]
        
        # Create backend structure
        (self.output_dir / 'backend' / 'models').mkdir(parents=True)
        (self.output_dir / 'backend' / 'routes').mkdir(parents=True)
        (self.output_dir / 'backend' / 'utils').mkdir(parents=True)
        (self.output_dir / 'frontend').mkdir(parents=True)
        
        for file_path in base_files:
            src = self.template_dir / file_path
            dst = self.output_dir / file_path
            
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ {file_path}")
            else:
                print(f"  ⚠ {file_path} not found, skipping")
    
    def _generate_config_files(self):
        """Generate configuration files"""
        print("⚙️  Generating configuration files...")
        
        # Generate template_config.json
        config_file = self.output_dir / 'template_config.json'
        self.config.save_to_file(str(config_file))
        print(f"  ✓ template_config.json")
        
        # Generate .env template
        env_template = self._generate_env_template()
        with open(self.output_dir / '.env.template', 'w') as f:
            f.write(env_template)
        print(f"  ✓ .env.template")
        
        # Update backend config.py with template variables
        self._update_backend_config()
        print(f"  ✓ Updated backend/config.py")
    
    def _generate_env_template(self) -> str:
        """Generate .env template file"""
        env_content = f"""# {self.config.branding.app_name} Configuration
# Copy this file to .env and fill in your actual values

# Application
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///{self.config.database.sqlite_db_name}

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Application Branding
APP_NAME="{self.config.branding.app_name}"
APP_TAGLINE="{self.config.branding.app_tagline}"
APP_DESCRIPTION="{self.config.branding.app_description}"
SUPPORT_EMAIL="{self.config.branding.support_email}"
"""
        
        # Add integration-specific variables
        if self.config.integrations.bank_integration_enabled:
            if self.config.integrations.bank_provider == "akahu":
                env_content += """
# Akahu Bank Integration
AKAHU_CLIENT_ID=your-akahu-client-id
AKAHU_CLIENT_SECRET=your-akahu-client-secret
"""
        
        if self.config.integrations.payment_integration_enabled:
            if self.config.integrations.payment_provider == "stripe":
                env_content += """
# Stripe Payment Integration
STRIPE_PUBLISHABLE_KEY=pk_test_your-publishable-key
STRIPE_SECRET_KEY=sk_test_your-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
"""
        
        return env_content
    
    def _update_backend_config(self):
        """Update backend config.py with template variables"""
        config_path = self.output_dir / 'backend' / 'config.py'
        
        config_content = f'''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///{self.config.database.sqlite_db_name}'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    
    # Application branding
    APP_NAME = os.environ.get('APP_NAME') or '{self.config.branding.app_name}'
    APP_TAGLINE = os.environ.get('APP_TAGLINE') or '{self.config.branding.app_tagline}'
    APP_DESCRIPTION = os.environ.get('APP_DESCRIPTION') or '{self.config.branding.app_description}'
    APP_EMOJI = '{self.config.branding.app_emoji}'
    COMPANY_NAME = '{self.config.branding.company_name}'
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL') or '{self.config.branding.support_email}'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Authentication settings
    EMAIL_VERIFICATION_REQUIRED = {str(self.config.auth.require_email_verification).lower()}
    PASSWORD_MIN_LENGTH = {self.config.auth.password_min_length}
    EMAIL_VERIFICATION_TOKEN_EXPIRES = {self.config.auth.email_verification_token_expires}
    PASSWORD_RESET_TOKEN_EXPIRES = {self.config.auth.password_reset_token_expires}
'''
        
        # Add integration configurations
        if self.config.integrations.bank_integration_enabled:
            if self.config.integrations.bank_provider == "akahu":
                config_content += '''
    # Akahu bank integration
    AKAHU_CLIENT_ID = os.environ.get('AKAHU_CLIENT_ID')
    AKAHU_CLIENT_SECRET = os.environ.get('AKAHU_CLIENT_SECRET')
'''
        
        if self.config.integrations.payment_integration_enabled:
            if self.config.integrations.payment_provider == "stripe":
                config_content += '''
    # Stripe payment integration
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
'''
        
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    def _update_branding(self):
        """Update branding throughout the application"""
        print("🎨 Updating branding...")
        
        # Update frontend HTML
        self._update_frontend_html()
        
        # Update app.py welcome message
        self._update_app_py()
        
        print(f"  ✓ Updated branding to: {self.config.branding.app_name}")
    
    def _update_frontend_html(self):
        """Update frontend HTML with new branding"""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#3498db">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{self.config.branding.app_name}">
    <meta name="description" content="{self.config.branding.meta_description}">
    <meta name="keywords" content="{self.config.branding.meta_keywords}">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{self.config.branding.app_emoji}</text></svg>">
    <link rel="manifest" href="manifest.json">
    <title>{self.config.branding.meta_title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{self.config.branding.app_emoji} {self.config.branding.app_name}</h1>
            <p>{self.config.branding.app_tagline}</p>
        </header>
        
        <main>
            <div class="welcome-card">
                <h2>Welcome to {self.config.branding.app_name}</h2>
                <p>{self.config.branding.app_description}</p>
                
                <div class="auth-buttons">
                    <button class="btn btn-primary" onclick="showLogin()">Log In</button>
                    <button class="btn btn-secondary" onclick="showSignup()">Sign Up</button>
                </div>
            </div>
            
            <div id="loginForm" class="auth-form hidden">
                <h3>Log In</h3>
                <form>
                    <input type="email" placeholder="Email" required>
                    <input type="password" placeholder="Password" required>
                    <button type="submit" class="btn btn-primary">Log In</button>
                </form>
                <p><a href="#" onclick="showSignup()">Don't have an account? Sign up</a></p>
            </div>
            
            <div id="signupForm" class="auth-form hidden">
                <h3>Create Account</h3>
                <form>
                    <input type="email" placeholder="Email" required>
                    <input type="password" placeholder="Password (min 8 characters)" required minlength="8">
                    <input type="password" placeholder="Confirm Password" required>
                    <button type="submit" class="btn btn-primary">Create Account</button>
                </form>
                <p><a href="#" onclick="showLogin()">Already have an account? Log in</a></p>
            </div>
        </main>
        
        <footer>
            <p>&copy; 2024 {self.config.branding.company_name}. {self.config.branding.app_name}.</p>
        </footer>
    </div>
    
    <script src="app.js"></script>
</body>
</html>'''
        
        with open(self.output_dir / 'frontend' / 'index.html', 'w') as f:
            f.write(html_content)
    
    def _update_app_py(self):
        """Update app.py with new branding"""
        app_path = self.output_dir / 'backend' / 'app.py'
        
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Replace the welcome message
        content = content.replace(
            '"message": "Rent Check API is running!"',
            f'"message": "{self.config.branding.app_name} API is running!"'
        )
        
        with open(app_path, 'w') as f:
            f.write(content)
    
    def _generate_database_schema(self):
        """Generate database schema based on configuration"""
        print("🗄️  Generating database schema...")
        
        # Create database initialization script
        self._create_database_init_script()
        
        # Generate feature module models
        self._generate_feature_models()
        
        print(f"  ✓ Database schema generated")
    
    def _create_database_init_script(self):
        """Create database initialization script"""
        tables = self.config.get_all_database_tables()
        
        init_content = f'''import sqlite3
import os
from datetime import datetime

DATABASE_PATH = '{self.config.database.sqlite_db_name}'

def get_db_connection():
    """Get a database connection using SQLite"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        return conn
    except Exception as e:
        print(f"Database connection error: {{e}}")
        return None

def test_db_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            return result['test'] == 1
        return False
    except Exception as e:
        print(f"Database test failed: {{e}}")
        return False

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Users table (core)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User sessions table (core)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notification log table (core)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                notification_type TEXT NOT NULL,
                date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                status TEXT DEFAULT 'sent'
            )
        """)
'''
        
        # Add feature-specific tables
        for module in self.config.get_enabled_modules():
            init_content += f'''
        # {module.display_name} tables
'''
            for table in module.tables:
                if table == 'properties':
                    init_content += '''
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT,
                data JSON,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)'''
                elif table == 'transactions':
                    init_content += '''
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER REFERENCES properties(id),
                user_id INTEGER REFERENCES users(id),
                date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                type TEXT DEFAULT 'income',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)'''
                # Add more table templates as needed
        
        init_content += '''
        conn.commit()
        print("Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if test_db_connection():
        print("Database connection successful")
        init_db()
    else:
        print("Database connection failed")'''
        
        with open(self.output_dir / 'backend' / 'database_init.py', 'w') as f:
            f.write(init_content)
    
    def _generate_feature_models(self):
        """Generate model files for feature modules"""
        for module in self.config.get_enabled_modules():
            model_path = self.output_dir / 'backend' / 'models' / f'{module.name}.py'
            
            model_content = f'''"""
{module.display_name} Model
Generated by SaaS Template Generator
"""

from database_sqlite import get_db_connection
from datetime import datetime

class {module.name.title().replace('_', '')}:
    """Model for {module.display_name}"""
    
    def __init__(self, id=None, user_id=None, name=None, description=None, data=None, status='active', created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.data = data or {{}}
        self.status = status
        self.created_at = created_at
    
    @staticmethod
    def create(user_id, name, description=None, data=None):
        """Create a new {module.name} record"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO {module.tables[0] if module.tables else 'items'} (user_id, name, description, data, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, name, description, str(data) if data else None, 'active', datetime.now()))
            
            item_id = cursor.lastrowid
            conn.commit()
            
            # Return the created item
            return {module.name.title().replace('_', '')}.get_by_id(item_id)
            
        except Exception as e:
            print(f"Error creating {module.name}: {{e}}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all {module.name} records for a user"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM {module.tables[0] if module.tables else 'items'} 
                WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            items = []
            
            for result in results:
                items.append({module.name.title().replace('_', '')}(
                    id=result['id'],
                    user_id=result['user_id'],
                    name=result['name'],
                    description=result['description'],
                    data=eval(result['data']) if result['data'] else {{}},
                    status=result['status'],
                    created_at=result['created_at']
                ))
            
            return items
        except Exception as e:
            print(f"Error getting {module.name} by user ID: {{e}}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(item_id):
        """Get {module.name} by ID"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM {module.tables[0] if module.tables else 'items'} WHERE id = ?
            """, (item_id,))
            
            result = cursor.fetchone()
            if result:
                return {module.name.title().replace('_', '')}(
                    id=result['id'],
                    user_id=result['user_id'],
                    name=result['name'],
                    description=result['description'],
                    data=eval(result['data']) if result['data'] else {{}},
                    status=result['status'],
                    created_at=result['created_at']
                )
            return None
        except Exception as e:
            print(f"Error getting {module.name} by ID: {{e}}")
            return None
        finally:
            conn.close()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {{
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'data': self.data,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None
        }}
'''
            
            with open(model_path, 'w') as f:
                f.write(model_content)
    
    def _generate_feature_modules(self):
        """Generate route handlers for feature modules"""
        print("🔧 Generating feature modules...")
        
        for module in self.config.get_enabled_modules():
            self._generate_module_routes(module)
            print(f"  ✓ {module.display_name}")
    
    def _generate_module_routes(self, module):
        """Generate routes for a specific module"""
        route_path = self.output_dir / 'backend' / 'routes' / f'{module.name}.py'
        
        route_content = f'''"""
{module.display_name} Routes
Generated by SaaS Template Generator
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.{module.name} import {module.name.title().replace('_', '')}

{module.name}_bp = Blueprint('{module.name}', __name__, url_prefix='{module.api_prefix}/{module.name}')

@{module.name}_bp.route('/', methods=['GET'])
@login_required
def get_{module.name}():
    """Get all {module.name} items for the current user"""
    try:
        items = {module.name.title().replace('_', '')}.get_by_user_id(current_user.id)
        return jsonify({{
            'items': [item.to_dict() for item in items]
        }}), 200
    except Exception as e:
        print(f"Error getting {module.name}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500

@{module.name}_bp.route('/', methods=['POST'])
@login_required
def create_{module.name}():
    """Create a new {module.name} item"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        item_data = data.get('data', {{}})
        
        if not name:
            return jsonify({{'error': 'Name is required'}}), 400
        
        item = {module.name.title().replace('_', '')}.create(
            user_id=current_user.id,
            name=name,
            description=description,
            data=item_data
        )
        
        if not item:
            return jsonify({{'error': 'Failed to create {module.name}'}}), 500
        
        return jsonify({{
            'message': '{module.display_name} created successfully',
            'item': item.to_dict()
        }}), 201
        
    except Exception as e:
        print(f"Error creating {module.name}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500

@{module.name}_bp.route('/<int:item_id>', methods=['GET'])
@login_required
def get_{module.name}_by_id(item_id):
    """Get a specific {module.name} item"""
    try:
        item = {module.name.title().replace('_', '')}.get_by_id(item_id)
        
        if not item:
            return jsonify({{'error': '{module.display_name} not found'}}), 404
        
        # Verify ownership
        if item.user_id != current_user.id:
            return jsonify({{'error': 'Access denied'}}), 403
        
        return jsonify({{'item': item.to_dict()}}), 200
        
    except Exception as e:
        print(f"Error getting {module.name} by ID: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500
'''
        
        with open(route_path, 'w') as f:
            f.write(route_content)
        
        # Update main app.py to register the blueprint
        self._register_blueprint(module)
    
    def _register_blueprint(self, module):
        """Register the module blueprint in main app.py"""
        app_path = self.output_dir / 'backend' / 'app.py'
        
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Add import and registration
        import_line = f"from routes.{module.name} import {module.name}_bp"
        register_line = f"app.register_blueprint({module.name}_bp)"
        
        # Add the import after other route imports
        if "from routes.properties import properties_bp" in content:
            content = content.replace(
                "from routes.properties import properties_bp",
                f"from routes.properties import properties_bp\n{import_line}"
            )
            content = content.replace(
                "app.register_blueprint(properties_bp)",
                f"app.register_blueprint(properties_bp)\n{register_line}"
            )
        else:
            # Add after auth import
            content = content.replace(
                "app.register_blueprint(auth_bp)",
                f"app.register_blueprint(auth_bp)\n{import_line}\n{register_line}"
            )
        
        with open(app_path, 'w') as f:
            f.write(content)
    
    def _generate_frontend(self):
        """Generate frontend components"""
        print("🎨 Generating frontend components...")
        
        # Generate manifest.json
        manifest_content = {
            "name": self.config.branding.app_name,
            "short_name": self.config.branding.app_name,
            "description": self.config.branding.app_description,
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#3498db",
            "icons": []
        }
        
        with open(self.output_dir / 'frontend' / 'manifest.json', 'w') as f:
            json.dump(manifest_content, f, indent=2)
        
        print(f"  ✓ Generated PWA manifest")
    
    def _generate_documentation(self):
        """Generate setup and usage documentation"""
        print("📚 Generating documentation...")
        
        readme_content = f"""# {self.config.branding.app_name}

{self.config.branding.app_description}

## Features

- 🔐 Complete authentication system (login, signup, email verification, password reset)
- 👤 User management with Flask-Login integration
- 🗄️  SQLite/PostgreSQL dual database support
- ✉️  Email service integration
- 📱 Responsive PWA-ready frontend
- 🔧 Modular architecture for easy customization

## Enabled Modules

"""
        
        for module in self.config.get_enabled_modules():
            readme_content += f"- **{module.display_name}**: {module.description}\n"
        
        readme_content += f"""

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r backend/requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**
   ```bash
   cd backend
   python database_init.py
   ```

4. **Run Application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Configuration

This application is generated from a template configuration. You can customize:

- **Branding**: App name, description, colors, etc.
- **Authentication**: Password requirements, email verification settings
- **Features**: Enable/disable modules, add custom functionality
- **Integrations**: Payment processors, email providers, analytics

### Template Configuration

The `template_config.json` file contains all customizable settings:

```json
{{
  "branding": {{
    "app_name": "{self.config.branding.app_name}",
    "app_tagline": "{self.config.branding.app_tagline}",
    ...
  }},
  "auth": {{
    "require_email_verification": {str(self.config.auth.require_email_verification).lower()},
    "password_min_length": {self.config.auth.password_min_length},
    ...
  }},
  ...
}}
```

## Development

### Project Structure

```
{self.config.branding.app_name.lower().replace(' ', '-')}/
├── backend/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── utils/           # Utility functions
│   ├── app.py          # Main application
│   └── config.py       # Configuration
├── frontend/
│   ├── index.html      # Main HTML file
│   ├── app.js          # JavaScript logic
│   └── styles.css      # Styling
└── template_config.json # Template configuration
```

### Adding Features

1. Create new models in `backend/models/`
2. Add routes in `backend/routes/`
3. Register blueprints in `app.py`
4. Update frontend components as needed

## Deployment

### Environment Variables

See `.env.template` for all required environment variables.

### Database

- Development: SQLite (default)
- Production: PostgreSQL (recommended)

Update `DATABASE_URL` in your environment variables.

## Support

For support and questions:
- Email: {self.config.branding.support_email}
- Documentation: See this README

## License

Generated from SaaS Template Generator
"""
        
        with open(self.output_dir / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print(f"  ✓ Generated README.md")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='SaaS Template Generator')
    parser.add_argument('template_type', choices=['rent', 'subscription', 'project', 'custom'], 
                       help='Type of SaaS template to generate')
    parser.add_argument('output_dir', help='Output directory for generated template')
    parser.add_argument('--config', help='Custom configuration file (JSON)')
    parser.add_argument('--overwrite', action='store_true', 
                       help='Overwrite output directory if it exists')
    
    args = parser.parse_args()
    
    # Create template configuration
    if args.template_type == 'rent':
        config = create_rent_tracking_config()
    elif args.template_type == 'subscription':
        config = create_subscription_saas_config()
    elif args.template_type == 'project':
        config = create_project_management_config()
    elif args.template_type == 'custom':
        if not args.config:
            print("Custom template requires --config parameter")
            return 1
        config = SaaSTemplate(args.config)
    
    # Generate template
    generator = TemplateGenerator(config)
    
    success = generator.generate(args.output_dir, overwrite=args.overwrite)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())