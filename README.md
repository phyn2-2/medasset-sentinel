# MedAsset Sentinel

**Hospital Equipment Maintenance & Monitoring System**

A comprehensive maintenance management system for biomedical equipment in healthcare facilities. Integrates preventive maintenance scheduling, real-time equipment monitoring, intelligent alerting, and compliance audit trails.

---

## 🎯 Project Overview

### Problem Statement
Hospitals must track biomedical equipment, schedule preventive maintenance, respond to equipment failures, and maintain audit trails for compliance and patient safety. Manual processes are error-prone and lack real-time visibility.

### Solution
MedAsset Sentinel provides:
- **Automated maintenance scheduling** with preventive alerts
- **Real-time equipment monitoring** (simulated IoT sensors)
- **Intelligent alerting system** for failures and overdue maintenance
- **Compliance audit trails** for regulatory requirements
- **Administrative dashboard** for operational oversight

---

## 🏗️ System Architecture

### Technology Stack
- **Backend:** Python 3.x, Flask
- **ORM:** SQLAlchemy
- **Database:** SQLite (Phase 1) → PostgreSQL-ready
- **Scheduler:** APScheduler (background jobs)
- **Authentication:** Flask-Login (session-based)
- **Frontend:** Jinja2 templates, CSS

### Design Principles
- **Layered Architecture:** Routes → Services → Models (no logic in routes)
- **Separation of Concerns:** Equipment status ≠ Maintenance status
- **Audit Trail Integrity:** Append-only logs, resolution-only alerts
- **Scheduler-Driven Intelligence:** Autonomous maintenance checks and IoT monitoring

---

## 📊 Data Model

### Core Entities
- **Equipment:** Central registry with operational status and maintenance schedules
- **MaintenanceLog:** Permanent audit trail of all maintenance actions
- **Alert:** First-class notifications (maintenance, failures)
- **SensorEvent:** IoT telemetry history (time-series data)
- **Admin:** Authentication and access control

### Key Relationships
```
Equipment (1) → (N) MaintenanceLog  [CASCADE]
Equipment (1) → (N) Alert           [SET NULL - audit preservation]
Equipment (1) → (N) SensorEvent     [CASCADE]
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/phyn2-2/medasset-sentinel.git
cd medasset-sentinel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 app.py  # Creates tables automatically

# Seed initial data (admin + sample equipment)
python3 seed.py
```

### Default Credentials
```
Username: admin
Password: admin123
```
⚠️ **Change in production!**

---

## 📁 Project Structure

```
medasset_sentinel/
├── app.py                  # Application factory & entry point
├── config.py               # Configuration management
├── extensions.py           # Flask extensions (db, scheduler)
├── models.py               # SQLAlchemy ORM models
├── seed.py                 # Database seeding script
│
├── services/               # Business logic layer
│   ├── auth_service.py
│   ├── equipment_service.py
│   ├── maintenance_service.py
│   └── alert_service.py
│
├── routes/                 # Flask routes (presentation layer)
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   └── equipment_routes.py
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── equipment.html
│
├── static/                 # CSS, JS, images
│   └── style.css
│
└── requirements.txt        # Python dependencies
```

---

## 🔧 Development Phases

### ✅ Phase 1: Foundation (Complete)
- [x] Project structure
- [x] Database models (SQLAlchemy)
- [x] Configuration management
- [x] Database seeding

### 🚧 Phase 2: Core Logic (In Progress)
- [ ] Authentication service
- [ ] Equipment CRUD service
- [ ] Maintenance scheduling service
- [ ] Alert management service

### 📋 Phase 3: Automation
- [ ] Background scheduler setup
- [ ] Maintenance check jobs (daily)
- [ ] IoT monitoring simulation (30s intervals)
- [ ] Automated alert generation

### 🎨 Phase 4: Dashboard & UI
- [ ] Admin dashboard
- [ ] Equipment management views
- [ ] Alert resolution interface
- [ ] Maintenance logging forms

---

## 🎓 Learning Outcomes

This project demonstrates:
- **System Design:** Layered architecture, separation of concerns
- **ORM Proficiency:** SQLAlchemy with complex relationships
- **Background Processing:** Scheduled jobs, autonomous system behavior
- **Domain Modeling:** Real-world operational system (CMMS-style)
- **Data Integrity:** Audit trails, cascade rules, constraint design
- **Extensibility:** SQLite → PostgreSQL migration, real IoT integration readiness

---

## 📝 Key Design Decisions

### Why Equipment Status ≠ Maintenance Status?
Equipment can fail even if maintenance is current (operational failure). Maintenance can be overdue even if equipment is working (compliance risk). These are independent concerns.

### Why Are Alerts Never Deleted?
Healthcare systems require audit trails. Resolved alerts preserve compliance history and root cause analysis data for regulatory audits.

### Why SQLite for Phase 1?
Appropriate for development/demo scope. SQLAlchemy abstracts the database—migrating to PostgreSQL is a config change, not a code rewrite. Demonstrates pragmatism over premature optimization.

---

## 🔐 Security Notes

- Passwords stored as bcrypt hashes (never plaintext)
- Session-based authentication
- SQL injection protection via ORM
- **⚠️ Phase 1 is for development/demo only**
- Production deployment requires:
  - Environment-based secrets
  - HTTPS enforcement
  - Rate limiting
  - CSRF protection

---

## 🧪 Testing

```bash
# Run application
python3 app.py

# Access dashboard
http://localhost:5000

# Login with seeded credentials
Username: admin
Password: admin123
```

---

## 📚 Documentation

- [System Requirements Document](docs/system-requirements.md)
- [Data Flow Diagram](docs/data-flow-diagram.md)
- [Database Schema](docs/database-schema.md)

---

## 🚀 Future Enhancements

- [ ] Email/SMS alert notifications
- [ ] Technician role and task assignment
- [ ] Equipment purchase/warranty tracking
- [ ] CSV export and reporting
- [ ] Real IoT sensor integration (MQTT, Raspberry Pi)
- [ ] Mobile application
- [ ] Multi-tenant support

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 👤 Author

**[Your Name]**
- GitHub: [@phyn2-2](https://github.com/yourusername)
- LinkedIn: [Baphyn Magero](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

Built as a capstone project demonstrating:
- Backend system design
- Real-world operational system architecture
- Healthcare compliance awareness
- Professional engineering practices

---

**MedAsset Sentinel** - Intelligent Equipment Maintenance for Healthcare
