# JanGeo – Citizen & Government Geolocation Reporting System

JanGeo is a multilingual e-governance platform designed for both citizens and government departments. It enables real-time GPS-based infrastructure issue reporting, departmental routing, map visualization, workflow tracking, data export, and Power BI analytics. A Power BI dashboard sample is included in this repository.

---

## 1. Problem Statement
Infrastructure issues—such as potholes, water leaks, electricity outages, and garbage overflow—often remain unresolved due to:

- No unified reporting system  
- Citizens not knowing which department handles which issue  
- Lack of geolocation, photos, and timestamps  
- No transparent tracking mechanism  
- Government workflows operating in isolation  

JanGeo solves these problems by allowing citizens to report issues instantly using geolocation while enabling government teams to track, manage, and resolve problems efficiently.

---

## 2. Project Overview
JanGeo enables citizens to submit incidents with automatically captured GPS coordinates, descriptions, and photos. Government departments receive and manage these reports through an interactive dashboard. Data can be exported for analytics, including Power BI.

**Core Data Flow (Inside System):**

**Citizen Device → Streamlit Interface → MySQL Database → Government Dashboard → MySQL → Power BI Dashboard**

This closed loop ensures accurate issue reporting, efficient departmental action, and insight generation through analytics.

---

## 3. Key Features

### 3.1 Citizen Features
- Secure registration & login (SHA-256 password hashing)  
- Mandatory data-consent workflow  
- Submit issue reports with:
  - Auto GPS location  
  - Descriptions  
  - Photo uploads  
  - Department selection  
- View previously submitted issues  
- Submit feedback after issue resolution  

### 3.2 Government Features
- Department-wise dashboards (Roads, Water, Electricity, Sanitation, Other)  
- Interactive Folium map with markers for all reported issues  
- Status update workflow: Pending → In Progress → Resolved  
- Export data as CSV, Excel, or Parquet  
- Integration-ready for Power BI (sample dashboard included)

### 3.3 Multilingual Interface
Supported languages:
- English  
- Hindi  
- Telugu  
- Tamil  
- Kannada  
- Malayalam  

### 3.4 Mapping & Visualization
- Folium map embedded in Streamlit  
- Popups showing issue details  
- Auto-centering based on available reports  

### 3.5 Feedback System
Citizens can provide feedback on resolved issues, enabling performance evaluation and accountability for government departments.

---

## 4. Approach

### Conceptual Approach
JanGeo (जन + Geo → People + Location) connects citizens and departments through:

1. Real-time geo-tagged reporting  
2. Automatic routing to responsible departments  
3. Transparent progress tracking  
4. Structured data for analytics  
5. Multilingual accessibility  

### Technical Approach
- Streamlit frontend for reporting, dashboards, and feedback  
- MySQL backend for secure storage  
- Folium for geospatial visualization  
- Pandas & PyArrow for data export  
- SHA-256 password hashing & consent enforcement  
- Power BI dashboard for analytics (included in repo)

---

## 5. Methodology

### 1. Planning & Analysis
- Identified requirements of citizens and government workflows  
- Prioritized simplicity, transparency, and multilingual access  

### 2. Design

**Database tables:**
- `users`  
- `reports`  
- `feedbacks`  
- `id_counter`  

**UI Design:**
- Multilingual layout  
- Tab-based navigation  
- Accessibility features (e.g., high-contrast mode)

### 3. Development

**Tools Used:**
- Streamlit  
- MySQL Connector  
- Folium  
- Pandas, PyArrow  
- PIL  

**Core Functions:**
- `register_user()`  
- `login_user()`  
- `generate_id()`  
- `submit_report()`  
- `update_status()`  
- `export_data()`  

### 4. Testing
- Verified full workflow from report creation to Power BI export  
- Ensured multilingual rendering and map accuracy  
- Tested geolocation capture & file uploads  

### 5. Deployment Readiness
- Ready for deployment on Streamlit Cloud / Heroku  
- Database structure adaptable to PostgreSQL  
- Modular design for future upgrades (AI-based classification, heatmaps, automation)

---

## 6. Database Schema

### `users`
- id (PK)  
- username  
- password (SHA-256)  
- consent (boolean)  

### `reports`
- id (PK)  
- user_id  
- issue_type  
- description  
- latitude  
- longitude  
- timestamp  
- photo (binary)  
- department  
- status  

### `feedbacks`
- id (PK)  
- report_id  
- feedback  
- timestamp  

### `id_counter`
- entity_type  
- last_number  

---

## Conclusion
JanGeo provides a complete digital governance workflow by connecting citizens, departments, and analytics systems. The integration of multilingual reporting, GPS-based data capture, departmental dashboards, MySQL storage, and Power BI analytics makes JanGeo a scalable foundation for smart-city governance. The included Power BI sample demonstrates how exported data translates into actionable insights across departments.
