#!/usr/bin/env python3
"""
Quick SaaS Template Generator
Simple script for common template types
"""

import sys
from template_generator import TemplateGenerator
from template_config import (
    create_rent_tracking_config,
    create_subscription_saas_config, 
    create_project_management_config
)

def print_usage():
    print("SaaS Template Generator")
    print("=" * 30)
    print()
    print("Usage:")
    print("  python generate.py <template_type> <output_directory>")
    print()
    print("Available templates:")
    print("  rent        - Rent tracking/property management SaaS")
    print("  subscription - Subscription tracking SaaS")
    print("  project     - Project management SaaS")
    print()
    print("Examples:")
    print("  python generate.py rent my-rent-app")
    print("  python generate.py subscription subscription-tracker")
    print("  python generate.py project project-hub")
    print()
    print("For custom configuration:")
    print("  python setup_template.py")

def main():
    if len(sys.argv) != 3 or sys.argv[1] in ['--help', '-h', 'help']:
        print_usage()
        return 0 if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h', 'help'] else 1
    
    template_type = sys.argv[1].lower()
    output_dir = sys.argv[2]
    
    # Create template configuration
    if template_type == 'rent':
        config = create_rent_tracking_config()
        print(f"🏠 Generating rent tracking SaaS template...")
    elif template_type == 'subscription':
        config = create_subscription_saas_config()
        print(f"📊 Generating subscription management SaaS template...")
    elif template_type == 'project':
        config = create_project_management_config()
        print(f"📋 Generating project management SaaS template...")
    else:
        print(f"❌ Unknown template type: {template_type}")
        print()
        print_usage()
        return 1
    
    # Generate template
    generator = TemplateGenerator(config)
    success = generator.generate(output_dir, overwrite=False)
    
    if not success:
        print(f"❌ Failed to generate template in {output_dir}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())