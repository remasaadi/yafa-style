# Yafa Style Boutique Management System

## Overview

Yafa Style Boutique is a web-based retail management system developed using Python, Flask, and SQLite.

The system was designed to help manage customers, employees, transactions, and loyalty points for a clothing boutique. It provides an intuitive interface for daily business operations and customer relationship management.

---

## Features

- Customer management
- Employee management
- Secure authentication and login system
- Loyalty points tracking
- Transaction management
- Points redemption system
- Daily transaction reports
- Role-based access control (Admin/User)
- SQLite database integration

---

## Technologies Used

### Backend
- Python
- Flask
- Flask-Login
- SQLAlchemy

### Database
- SQLite

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Software Engineering Concepts
- MVC Architecture
- Authentication & Authorization
- Database Design
- CRUD Operations
- Business Logic Implementation

---

## System Modules

### Authentication
- User login
- Password management
- Session handling

### Customer Management
- Add customers
- Search customers
- Track loyalty points

### Transaction Management
- Add transactions
- Calculate earned points
- Redeem existing points
- Store transaction history

### Reporting
- Daily transaction reports
- Employee transaction tracking

### Administration
- Employee management
- User role management

---

## Database Structure

Main entities include:

- Users
- Clients
- Transactions

The application uses SQLite and SQLAlchemy ORM for data persistence.

---

## Project Structure

```text
YaffaWebsite
│
├── main.py
├── website
│   ├── __init__.py
│   ├── auth.py
│   ├── models.py
│   ├── views.py
│   ├── templates/
│   └── static/
│
├── requirements.txt
├── README.md
└── .gitignore
