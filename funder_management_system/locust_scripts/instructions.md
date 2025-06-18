# Funder Management System Load Testing Documentation

## Overview
The `main_locust.py` file is a comprehensive load testing script built using the Locust framework to test the Funder Management System (FMS) application. This script simulates multiple users performing various operations on the system to evaluate performance, scalability, and reliability under load.

## Key Components

### 1. **User Authentication**
- Loads user credentials from `users.csv` file
- Implements automatic login functionality for each simulated user
- Cycles through available user accounts to distribute load

### 2. **Doctype Testing**
The script tests 20 different doctypes across 5 main modules:

#### **Budget Planning Module:**
- Budget Plan, Budget Plan Template, Budget Category, Budget Sub-Category

#### **Donor Acquisition Management Module:**
- Organisation Lead

#### **Engagement Module:**
- Engagement Checklist Master, Grant Agreement, Donor

#### **Funder Management System Module:**
- Preferred Means of Communication, Compliance Checklist, Source of Connection, Category, Thematic Area, Designation, Organisation POC, Organisation Details, Financial Year

#### **Organisation Tools Module:**
- Document List

#### **Utilisation Module:**
- Expense Item, Utilisation Record

### 3. **API Operations Tested**

#### **CRUD Operations:**
- **GET List**: Retrieves lists of records for all doctypes
- **GET Specific**: Fetches individual records by ID
- **PUT Update**: Modifies existing records with test data
- **POST Create**: Creates new records (currently commented out)

#### **Custom API Endpoints (15 endpoints):**
- Number card utilities (leads, conversion rates, churn rates)
- Financial metrics (funds received, expenditure, active donors/agreements)
- Dashboard data endpoints
- Utility functions for financial year management

### 4. **Load Distribution**
Tasks are weighted to simulate realistic usage patterns:
- **Weight 2**: GET operations (list and specific record retrieval)
- **Weight 1**: PUT operations (record updates)  
- **Weight 3**: Custom API endpoints (highest priority for dashboard/analytics)

### 5. **Test Data Generation**
- Generates realistic test data for different doctypes
- Uses randomization to avoid conflicts
- Includes proper data structures for expense items, categories, designations, and financial years

## Usage Scenario
This script simulates real-world usage where users:
1. Log into the system
2. Browse different modules and view record lists
3. Access specific records for detailed information
4. Update existing records with new information
5. Access dashboard analytics and reports
6. Retrieve system metrics and KPIs

## Performance Monitoring
The script tracks performance metrics for:
- Authentication success/failure rates
- Response times for all API endpoints
- Success/failure rates for CRUD operations
- Custom endpoint performance
- Module-specific performance characteristics

## Configuration
- **Wait Time**: 1-3 seconds between user actions (configurable)
- **User Pool**: Cyclic rotation through available user accounts
- **Error Handling**: Comprehensive response validation and error reporting
- **Naming Convention**: Organized by module for clear performance analysis