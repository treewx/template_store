# 🚀 SaaS Template Generator

Convert your rent checking application into a reusable SaaS template for creating different types of applications with the same robust foundation.

## ✨ What This Template Includes

**🔐 Complete Authentication System:**
- User registration and login
- Email verification 
- Password reset functionality
- Session management with Flask-Login
- Secure password hashing with bcrypt

**🗄️ Flexible Database Support:**
- SQLite for development
- PostgreSQL for production
- Automatic schema generation
- Database migration system

**📧 Email Integration:**
- Welcome emails
- Verification emails
- Password reset emails
- Customizable templates

**🎨 Responsive Frontend:**
- Mobile-friendly design
- PWA-ready with manifest.json
- Clean, modern CSS
- Interactive JavaScript

**🔌 Extensible Architecture:**
- Modular feature system
- Third-party integrations (Stripe, banking APIs, analytics)
- Easy customization and branding
- Configuration-driven setup

## 🚀 Quick Start

### Option 1: Pre-built Templates

Generate a complete SaaS application in seconds:

```bash
# Rent tracking SaaS (original)
python generate.py rent my-rent-app

# Subscription management SaaS
python generate.py subscription subscription-tracker

# Project management SaaS  
python generate.py project project-hub
```

### Option 2: Custom Interactive Setup

Create a fully customized SaaS:

```bash
python setup_template.py
```

Follow the interactive prompts to configure:
- 📋 App branding and identity
- 🔐 Authentication requirements
- 🗄️ Database configuration
- 🔧 Custom feature modules
- 🔌 Third-party integrations

### Option 3: Advanced Configuration

For complex customizations:

```bash
# Create custom config
python -c "
from template_config import SaaSTemplate
template = SaaSTemplate()
# ... customize template ...
template.save_to_file('my_config.json')
"

# Generate from config
python template_generator.py custom my-app --config my_config.json
```

## 📁 Generated Structure

```
your-saas-app/
├── backend/
│   ├── models/              # Database models
│   │   ├── user.py         # User management
│   │   └── [custom].py     # Your feature modules
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   └── [custom].py     # Your feature routes
│   ├── utils/              # Utility functions
│   │   ├── email_service.py
│   │   └── notification_service.py
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── database_init.py    # Database setup
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main application
│   ├── app.js             # JavaScript logic
│   ├── styles.css         # Styling
│   └── manifest.json      # PWA manifest
├── template_config.json    # Template configuration
├── .env.template          # Environment variables template
└── README.md              # Setup instructions
```

## 🛠️ Development Workflow

1. **Generate your template:**
   ```bash
   python generate.py [template_type] [output_dir]
   cd [output_dir]
   ```

2. **Set up environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Configure application:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

4. **Initialize database:**
   ```bash
   cd backend
   python database_init.py
   ```

5. **Run application:**
   ```bash
   python app.py
   ```

   Visit `http://localhost:5000` to see your SaaS!

## 🎨 Customization Examples

### Rent Tracking SaaS (Original)
- 🏠 Property management
- 💰 Rent payment tracking
- 🏦 Bank integration (Akahu)
- 📧 Late payment notifications

### Subscription Management SaaS
- 📊 Subscription tracking
- 💳 Payment processing (Stripe)  
- 📈 Usage analytics
- 🔔 Renewal reminders

### Project Management SaaS
- 📋 Project and task management
- 👥 Team collaboration
- 📊 Progress tracking
- 📈 Analytics integration

### Your Custom SaaS
- ⚙️ Define your own features
- 🗄️ Custom database models
- 🎨 Branded interface
- 🔌 Required integrations

## 🔌 Available Integrations

**💰 Payment Processing:**
- Stripe
- PayPal
- Square

**🏦 Banking/Financial:**
- Akahu (NZ)
- Plaid (US/CA)
- Yodlee

**📧 Email Marketing:**
- Mailchimp
- SendGrid
- Constant Contact

**📊 Analytics:**
- Google Analytics
- Mixpanel
- Amplitude

## ⚙️ Configuration Options

### Branding
```json
{
  "branding": {
    "app_name": "Your SaaS",
    "app_tagline": "Your tagline",
    "app_description": "Your description",
    "app_emoji": "🚀",
    "company_name": "Your Company",
    "support_email": "support@yourcompany.com"
  }
}
```

### Authentication
```json
{
  "auth": {
    "require_email_verification": true,
    "password_min_length": 8,
    "password_require_numbers": true,
    "password_require_letters": true,
    "password_require_symbols": false
  }
}
```

### Feature Modules
```json
{
  "feature_modules": {
    "property_management": {
      "name": "property_management",
      "display_name": "Property Management",
      "description": "Manage rental properties",
      "tables": ["properties", "transactions"],
      "frontend_routes": ["/properties", "/dashboard"]
    }
  }
}
```

## 🚀 Deployment

### Environment Variables
See the generated `.env.template` for all required variables:

- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `MAIL_*` - Email service configuration
- Integration-specific keys (Stripe, Akahu, etc.)

### Production Deployment

**Docker (Recommended):**
```bash
# Add to your generated app
FROM python:3.9-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

**Traditional Hosting:**
- Deploy `backend/` to your server
- Install Python dependencies
- Configure environment variables
- Set up reverse proxy (nginx/Apache)
- Configure database (PostgreSQL recommended)

## 📚 Examples & Use Cases

### 1. E-commerce SaaS
```bash
python setup_template.py
# Configure with:
# - Product catalog features
# - Order management
# - Payment processing (Stripe)
# - Inventory tracking
```

### 2. CRM SaaS
```bash
python setup_template.py
# Configure with:
# - Contact management
# - Deal pipeline
# - Email marketing integration
# - Analytics
```

### 3. Booking/Scheduling SaaS
```bash
python setup_template.py
# Configure with:
# - Calendar management
# - Appointment booking
# - Payment processing
# - Email notifications
```

## 🤝 Contributing

This template is designed to be extended. To add new features:

1. **Create a new feature module:**
   ```python
   from template_config import FeatureModule
   
   my_module = FeatureModule(
       name="my_feature",
       display_name="My Feature",
       description="Does something awesome",
       tables=["my_table"],
       frontend_routes=["/my-feature"]
   )
   ```

2. **Add to template configuration:**
   ```python
   template.add_feature_module(my_module)
   ```

3. **Generate and test:**
   ```bash
   python template_generator.py custom test-app --config my_config.json
   ```

## 📄 License

This template generator is provided as-is for creating SaaS applications. The generated applications are yours to use and modify as needed.

## 🆘 Support

- 📧 Issues: Create an issue in this repository
- 💬 Questions: Check the generated README.md in your app
- 📖 Documentation: This file and generated docs

---

**From Rent Checker to Any SaaS - Your Foundation is Ready! 🚀**