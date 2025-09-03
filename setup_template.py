#!/usr/bin/env python3
"""
SaaS Template Setup Script
Interactive setup for customizing the SaaS template
"""

import os
import sys
import json
from pathlib import Path
from template_config import SaaSTemplate, FeatureModule
from template_generator import TemplateGenerator

def get_user_input(prompt, default=None, choices=None):
    """Get user input with optional default and choices validation"""
    if choices:
        prompt += f" ({'/'.join(choices)})"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    
    while True:
        response = input(prompt).strip()
        
        if not response and default:
            return default
        
        if not response and not default:
            print("This field is required. Please enter a value.")
            continue
            
        if choices and response.lower() not in [c.lower() for c in choices]:
            print(f"Please choose from: {', '.join(choices)}")
            continue
            
        return response

def get_yes_no(prompt, default=True):
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes', 'true', '1']

def interactive_setup():
    """Interactive setup wizard"""
    print("🚀 SaaS Template Setup Wizard")
    print("=" * 50)
    print()
    
    # Initialize template
    template = SaaSTemplate()
    
    # Branding configuration
    print("📋 Application Branding")
    print("-" * 25)
    
    template.branding.app_name = get_user_input("App name", "My SaaS App")
    template.branding.app_tagline = get_user_input("App tagline", "Your customizable SaaS solution")
    template.branding.app_description = get_user_input(
        "App description", 
        "A complete SaaS solution with authentication, user management, and extensible features"
    )
    template.branding.app_emoji = get_user_input("App emoji", "🚀")
    template.branding.company_name = get_user_input("Company name", "Your Company")
    template.branding.support_email = get_user_input("Support email", "support@yourcompany.com")
    
    print()
    
    # Authentication configuration
    print("🔐 Authentication Settings")
    print("-" * 30)
    
    template.auth.require_email_verification = get_yes_no(
        "Require email verification for new users?", True
    )
    template.auth.password_min_length = int(get_user_input("Minimum password length", "8"))
    template.auth.password_require_numbers = get_yes_no("Require numbers in passwords?", True)
    template.auth.password_require_letters = get_yes_no("Require letters in passwords?", True)
    template.auth.password_require_symbols = get_yes_no("Require symbols in passwords?", False)
    
    print()
    
    # Database configuration
    print("🗄️  Database Configuration")
    print("-" * 30)
    
    db_type = get_user_input("Database type", "sqlite", ["sqlite", "postgresql"])
    template.database.default_db_type = db_type
    
    if db_type == "sqlite":
        template.database.sqlite_db_name = get_user_input("SQLite database filename", "app.db")
    
    print()
    
    # Feature modules
    print("🔧 Feature Modules")
    print("-" * 20)
    
    add_modules = get_yes_no("Add custom feature modules?", True)
    
    if add_modules:
        while True:
            print()
            module_name = get_user_input("Module name (e.g., 'property_management', 'task_tracking')")
            if not module_name:
                break
                
            module_display_name = get_user_input("Display name", module_name.replace('_', ' ').title())
            module_description = get_user_input("Module description", f"Manage {module_display_name.lower()}")
            
            # Ask for tables
            print("Database tables for this module (press Enter when done):")
            tables = []
            while True:
                table = get_user_input(f"  Table name ({len(tables)} added so far)")
                if not table:
                    break
                tables.append(table)
            
            # Ask for routes
            print("Frontend routes for this module (press Enter when done):")
            routes = []
            while True:
                route = get_user_input(f"  Route path ({len(routes)} added so far, e.g., '/dashboard')")
                if not route:
                    break
                if not route.startswith('/'):
                    route = '/' + route
                routes.append(route)
            
            module = FeatureModule(
                name=module_name,
                display_name=module_display_name,
                description=module_description,
                tables=tables,
                frontend_routes=routes
            )
            
            template.add_feature_module(module)
            print(f"✅ Added module: {module_display_name}")
            
            if not get_yes_no("Add another module?", False):
                break
    
    print()
    
    # Integrations
    print("🔌 Third-Party Integrations")
    print("-" * 35)
    
    # Banking integration
    if get_yes_no("Enable bank integration?", False):
        template.integrations.bank_integration_enabled = True
        template.integrations.bank_provider = get_user_input(
            "Bank provider", "akahu", ["akahu", "plaid", "yodlee"]
        )
    
    # Payment integration
    if get_yes_no("Enable payment processing?", False):
        template.integrations.payment_integration_enabled = True
        template.integrations.payment_provider = get_user_input(
            "Payment provider", "stripe", ["stripe", "paypal", "square"]
        )
    
    # Analytics
    if get_yes_no("Enable analytics?", False):
        template.integrations.analytics_enabled = True
        template.integrations.analytics_provider = get_user_input(
            "Analytics provider", "google", ["google", "mixpanel", "amplitude"]
        )
    
    # Email marketing
    if get_yes_no("Enable email marketing integration?", False):
        template.integrations.email_marketing_enabled = True
        template.integrations.email_marketing_provider = get_user_input(
            "Email marketing provider", "mailchimp", ["mailchimp", "sendgrid", "constant_contact"]
        )
    
    print()
    print("📁 Output Configuration")
    print("-" * 25)
    
    output_dir = get_user_input("Output directory", template.branding.app_name.lower().replace(' ', '-'))
    
    # Save configuration
    config_filename = f"{output_dir}_config.json"
    template.save_to_file(config_filename)
    
    print()
    print("✅ Configuration Summary")
    print("=" * 30)
    print(f"App Name: {template.branding.app_name}")
    print(f"Company: {template.branding.company_name}")
    print(f"Database: {template.database.default_db_type}")
    print(f"Feature Modules: {len(template.feature_modules)}")
    
    enabled_integrations = []
    if template.integrations.bank_integration_enabled:
        enabled_integrations.append(f"Bank ({template.integrations.bank_provider})")
    if template.integrations.payment_integration_enabled:
        enabled_integrations.append(f"Payments ({template.integrations.payment_provider})")
    if template.integrations.analytics_enabled:
        enabled_integrations.append(f"Analytics ({template.integrations.analytics_provider})")
    if template.integrations.email_marketing_enabled:
        enabled_integrations.append(f"Email Marketing ({template.integrations.email_marketing_provider})")
    
    print(f"Integrations: {', '.join(enabled_integrations) if enabled_integrations else 'None'}")
    print(f"Output Directory: {output_dir}")
    print(f"Configuration saved: {config_filename}")
    
    print()
    
    # Generate template
    if get_yes_no("Generate template now?", True):
        generator = TemplateGenerator(template)
        
        overwrite = False
        if Path(output_dir).exists():
            overwrite = get_yes_no(f"Directory '{output_dir}' exists. Overwrite?", False)
            if not overwrite:
                print("❌ Template generation cancelled.")
                return False
        
        success = generator.generate(output_dir, overwrite=overwrite)
        
        if success:
            print()
            print("🎉 Template generated successfully!")
            print(f"📂 Location: {Path(output_dir).absolute()}")
            print()
            print("🚀 Next steps:")
            print(f"   cd {output_dir}")
            print("   python -m venv venv")
            print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            print("   pip install -r backend/requirements.txt")
            print("   cp .env.template .env")
            print("   # Edit .env with your configuration")
            print("   cd backend && python database_init.py")
            print("   python app.py")
            return True
        else:
            print("❌ Template generation failed.")
            return False
    else:
        print(f"⏸️  Template configuration saved to {config_filename}")
        print(f"You can generate the template later using:")
        print(f"   python template_generator.py custom {output_dir} --config {config_filename}")
        return True

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("SaaS Template Setup Script")
        print()
        print("Usage:")
        print("  python setup_template.py           # Interactive setup")
        print("  python template_generator.py --help # Direct generation options")
        print()
        print("Available template types:")
        print("  - rent: Rent tracking/property management SaaS")
        print("  - subscription: Subscription tracking SaaS") 
        print("  - project: Project management SaaS")
        print("  - custom: Custom configuration (interactive)")
        return 0
    
    try:
        success = interactive_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())