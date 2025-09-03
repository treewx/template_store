"""
SaaS Template Configuration System
This file defines all the customizable aspects of the SaaS template
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AppBranding:
    """Application branding and identity configuration"""
    app_name: str = "SaaS Template"
    app_tagline: str = "Your customizable SaaS solution"
    app_description: str = "A complete SaaS template with authentication, user management, and extensible features"
    app_emoji: str = "🚀"
    company_name: str = "Your Company"
    support_email: str = "support@yourcompany.com"
    website_url: str = "https://yourcompany.com"
    
    # SEO and Meta
    meta_title: str = "SaaS Template - Complete Solution"
    meta_description: str = "A complete SaaS template with authentication, user management, and extensible features"
    meta_keywords: str = "saas, template, authentication, user management"

@dataclass 
class DatabaseConfig:
    """Database configuration options"""
    default_db_type: str = "sqlite"  # sqlite or postgresql
    sqlite_db_name: str = "app.db"
    
    # Core tables that will be created for any SaaS
    core_tables: List[str] = None
    
    def __post_init__(self):
        if self.core_tables is None:
            self.core_tables = ['users', 'user_sessions', 'notification_log']

@dataclass
class AuthConfig:
    """Authentication and user management configuration"""
    require_email_verification: bool = True
    password_min_length: int = 8
    password_require_numbers: bool = True
    password_require_letters: bool = True
    password_require_symbols: bool = False
    
    # Token expiration times (in seconds)
    email_verification_token_expires: int = 86400  # 24 hours
    password_reset_token_expires: int = 3600  # 1 hour
    
    # Login settings
    remember_me_duration: int = 2592000  # 30 days
    session_timeout: int = 3600  # 1 hour

@dataclass
class EmailConfig:
    """Email service configuration"""
    enabled: bool = True
    provider: str = "smtp"  # smtp, sendgrid, mailgun, etc.
    
    # Email templates
    welcome_email_template: str = "welcome_email.html"
    verification_email_template: str = "verification_email.html"
    password_reset_template: str = "password_reset.html"

@dataclass
class FeatureModule:
    """Configuration for a feature module (replaces rent-specific functionality)"""
    name: str
    display_name: str
    description: str
    enabled: bool = True
    
    # Database tables this module requires
    tables: List[str] = None
    
    # API endpoints this module exposes
    api_prefix: str = "/api"
    
    # Frontend routes this module handles
    frontend_routes: List[str] = None
    
    def __post_init__(self):
        if self.tables is None:
            self.tables = []
        if self.frontend_routes is None:
            self.frontend_routes = []

@dataclass
class IntegrationConfig:
    """Third-party integrations configuration"""
    # Banking/Financial APIs
    bank_integration_enabled: bool = False
    bank_provider: str = "akahu"  # akahu, plaid, yodlee, etc.
    
    # Payment processing
    payment_integration_enabled: bool = False
    payment_provider: str = "stripe"  # stripe, paypal, etc.
    
    # Analytics
    analytics_enabled: bool = False
    analytics_provider: str = "google"  # google, mixpanel, etc.
    
    # Email marketing
    email_marketing_enabled: bool = False
    email_marketing_provider: str = "mailchimp"  # mailchimp, sendgrid, etc.

class SaaSTemplate:
    """Main template configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.branding = AppBranding()
        self.database = DatabaseConfig()
        self.auth = AuthConfig()
        self.email = EmailConfig()
        self.integrations = IntegrationConfig()
        self.feature_modules: Dict[str, FeatureModule] = {}
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def add_feature_module(self, module: FeatureModule):
        """Add a feature module to the template"""
        self.feature_modules[module.name] = module
    
    def get_feature_module(self, name: str) -> Optional[FeatureModule]:
        """Get a feature module by name"""
        return self.feature_modules.get(name)
    
    def get_enabled_modules(self) -> List[FeatureModule]:
        """Get all enabled feature modules"""
        return [module for module in self.feature_modules.values() if module.enabled]
    
    def get_all_database_tables(self) -> List[str]:
        """Get all database tables needed by the template"""
        tables = self.database.core_tables.copy()
        
        for module in self.get_enabled_modules():
            tables.extend(module.tables)
        
        return list(set(tables))  # Remove duplicates
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary for JSON serialization"""
        return {
            'branding': self.branding.__dict__,
            'database': self.database.__dict__,
            'auth': self.auth.__dict__,
            'email': self.email.__dict__,
            'integrations': self.integrations.__dict__,
            'feature_modules': {
                name: module.__dict__ for name, module in self.feature_modules.items()
            }
        }
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        import json
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update branding
            if 'branding' in config_data:
                for key, value in config_data['branding'].items():
                    if hasattr(self.branding, key):
                        setattr(self.branding, key, value)
            
            # Update other configurations similarly
            for section in ['database', 'auth', 'email', 'integrations']:
                if section in config_data:
                    section_obj = getattr(self, section)
                    for key, value in config_data[section].items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
            
            # Load feature modules
            if 'feature_modules' in config_data:
                for name, module_data in config_data['feature_modules'].items():
                    module = FeatureModule(**module_data)
                    self.feature_modules[name] = module
                    
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""
        import json
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")


# Example configurations for different SaaS types

def create_rent_tracking_config() -> SaaSTemplate:
    """Create configuration for a rent tracking SaaS (original use case)"""
    template = SaaSTemplate()
    
    # Update branding
    template.branding.app_name = "Rent Check"
    template.branding.app_tagline = "Simple rent tracking for NZ landlords"
    template.branding.app_description = "Never miss a late rent payment again. Connect your bank account and get alerts when rent doesn't arrive on time."
    template.branding.app_emoji = "🏠"
    
    # Enable bank integration
    template.integrations.bank_integration_enabled = True
    template.integrations.bank_provider = "akahu"
    
    # Add property management module
    property_module = FeatureModule(
        name="property_management",
        display_name="Property Management",
        description="Manage rental properties and track payments",
        tables=["properties", "transactions"],
        frontend_routes=["/properties", "/dashboard"]
    )
    template.add_feature_module(property_module)
    
    return template

def create_subscription_saas_config() -> SaaSTemplate:
    """Create configuration for a subscription-based SaaS"""
    template = SaaSTemplate()
    
    # Update branding
    template.branding.app_name = "Subscription Manager"
    template.branding.app_tagline = "Manage your subscriptions effortlessly"
    template.branding.app_description = "Track, analyze, and optimize all your recurring subscriptions in one place."
    template.branding.app_emoji = "📊"
    
    # Enable payment integration
    template.integrations.payment_integration_enabled = True
    template.integrations.payment_provider = "stripe"
    
    # Add subscription tracking module
    subscription_module = FeatureModule(
        name="subscription_tracking",
        display_name="Subscription Tracking",
        description="Track and manage recurring subscriptions",
        tables=["subscriptions", "billing_cycles", "usage_metrics"],
        frontend_routes=["/subscriptions", "/analytics", "/billing"]
    )
    template.add_feature_module(subscription_module)
    
    return template

def create_project_management_config() -> SaaSTemplate:
    """Create configuration for a project management SaaS"""
    template = SaaSTemplate()
    
    # Update branding
    template.branding.app_name = "Project Hub"
    template.branding.app_tagline = "Streamline your project workflow"
    template.branding.app_description = "Organize, track, and collaborate on projects with your team efficiently."
    template.branding.app_emoji = "📋"
    
    # Enable analytics
    template.integrations.analytics_enabled = True
    template.integrations.analytics_provider = "google"
    
    # Add project management module
    project_module = FeatureModule(
        name="project_management",
        display_name="Project Management",
        description="Create and manage projects, tasks, and team collaboration",
        tables=["projects", "tasks", "team_members", "project_activities"],
        frontend_routes=["/projects", "/tasks", "/team", "/reports"]
    )
    template.add_feature_module(project_module)
    
    return template


# Default template instance
default_template = SaaSTemplate()