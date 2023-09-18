# Grocery_Store_Application_V2
MAD II Project IITM Sept 2023

This is basically an extension of the MAD I Project, which is stored [here](https://github.com/d-pamneja/Grocery_Store_Application_V1). So, here is how we can proceed:


Certainly, creating a project of this scope requires careful planning and a strategic approach to ensure timely and effective delivery. Here's a structured roadmap you can follow:

### **1. Pre-Planning (Days 1-2)**
- **Day 1:** Define project architecture and tech stack. Identify the major components and how they will communicate.
- **Day 2:** Set up your development environment:
  - Flask for the backend.
  - VueJS for the frontend.
  - SQLite for the database.
  - Redis for caching.
  - Redis & Celery for batch jobs.
  
### **2. Backend Development (Days 3-18)**
- **Days 3-5: User Management**
  - Set up Flask models for Users, Admin, and Store Managers with Role-Based Access Control (RBAC).
  - Implement JWT or Flask Security for authentication.
  - Design the database schema for SQLite.
- **Days 6-8: Section/Category Management**
  - Implement CRUD endpoints for sections/categories.
  - Add multilanguage support using UTF-8 encoding.
- **Days 9-11: Product Management**
  - Implement CRUD endpoints for products with multilanguage support.
  - Ensure the ability to allocate a product to a section/category.
- **Days 12-13: Shopping Cart & Product Purchase**
  - Design and implement a shopping cart model and related endpoints.
  - Implement purchase functionality.
- **Days 14-15: Backend Jobs**
  - Set up Celery for task scheduling.
  - Implement the daily reminder job using desired alert methods (e.g., Google Chat, SMS, Email).
  - Implement the monthly activity report.
- **Day 16-18: Performance, Caching, and Async Jobs**
  - Implement Redis for caching.
  - Integrate Celery for async operations like CSV exports.
  - Ensure API performance optimization.

### **3. Frontend Development (Days 19-28)**
- **Days 19-21: Setup & User Interface**
  - Set up VueJS with potential integration of Vue CLI.
  - Create the main layout using Bootstrap ensuring it's responsive.
- **Days 22-24: Admin & Store Manager UI**
  - Design and implement interfaces for product and category management.
  - Add features for CSV export.
- **Days 25-26: Shopping Cart UI**
  - Implement a shopping cart interface.
  - Ensure responsiveness.
- **Days 27-28: Reports and User Management UI**
  - Design interfaces for monthly reports in HTML and PDF.
  - Implement the user sign-up and login interfaces.

### **4. Advanced Features & Testing (Days 29-36)**
- **Days 29-30: Advanced Recommendations**
  - Implement the product reviews system.
  - Design an algorithm for predicting product popularity.
  - Set up promo codes for new users.
- **Days 31-33: Styling and Aesthetics**
  - Fine-tune UI/UX elements.
  - Ensure a uniform theme throughout the application.
- **Days 34-36: Testing**
  - Conduct unit tests on both backend and frontend.
  - Test all functionalities against the requirements.

### **5. Finalization and Documentation (Days 37-40)**
- **Days 37-38: Documentation**
  - Write comprehensive documentation covering setup, architecture, endpoints, and user manuals.
- **Day 39:** Dry Run
  - Simulate a complete workflow to ensure all components are functioning correctly.
- **Day 40:** Backup and Final Touches
  - Take backups.
  - Address any final issues or bugs.

**NOTE:** Depending on your pace and unforeseen challenges, the timeframe might slightly differ. Make sure to account for potential roadblocks and always have a backup plan. Allocate some buffer days for unexpected events. Make regular backups, and frequently commit your code to a version control system like Git.