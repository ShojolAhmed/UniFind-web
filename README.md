# UniFind

UniFind is a centralized, university-based Lost and Found web application designed to help students report, discover, and claim lost or found items across their campus. It provides a simple and structured platform to streamline item recovery, manage claims, and notify users internally.

---

## Features

- **User Authentication:** Account registration, login, and logout functionality.
- **Student Dashboard:** Central hub to manage personal item posts, view pending claims, and track claimed items.
- **Reporting System:** Report lost or found items with details such as title, description, location, item type, contact information, and image uploads.
- **Browse & Search:** Search available items by title or location, and filter listings by status (Lost / Found).
- **Claim Management:**
  - Submit claims for lost or found items.
  - Item owners receive internal notifications upon claim submission.
  - Owners can review, accept, or reject pending claims.
- **Post Management:** Edit or delete personal item posts.
- **Admin Panel:** Built-in Django administration interface for managing application data.

---

## Technology Stack

- **Backend:** Python, Django 4.2, SQLite
- **Frontend:** HTML, CSS, JavaScript, Django Templates
- **Additional:** WhiteNoise (static file serving), Pillow (image processing)

---

## Requirements

- **Python:** 3.10 or newer
- **Package Manager:** `pip`
- **Version Control:** Git

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/UniFind.git
cd UniFind
```

### 2. Create and Activate a Virtual Environment

- **Windows:**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Database Setup

Run the migrations to set up the SQLite database schema:

```bash
python manage.py migrate
```

---

## Admin Panel Setup

Create a superuser account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Once created, the admin panel can be accessed at `http://127.0.0.1:8000/admin/`.

---

## Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

Open your browser and navigate to:
`http://127.0.0.1:8000/`

---

## Application Workflow

1. **User Registration & Login:** Students register for an account and log in.
2. **Posting Items:** Users report a lost or found item by specifying details (title, description, location, type, contact info, and image).
3. **Browsing & Discovery:** Users browse, search, and filter listed items across campus.
4. **Submitting Claims:** A user submits a claim for an item they recognize or own.
5. **Notification:** The item owner receives an internal notification regarding the claim request.
6. **Resolution:** The owner reviews the claim details and accepts or rejects it.
7. **Dashboard Tracking:** Users track and manage their posts, active/pending claims, and resolved items via their dashboard.

---

## Admin Panel

The project leverages Django's built-in administration framework to manage application data, user permissions, and posts. Administrators can perform complete CRUD operations on models at `http://127.0.0.1:8000/admin/`.

---

## Future Improvements

- PostgreSQL support for database scalability
- Enhanced, responsive UI/UX design
- Advanced item filtering and category-based categorization
- Improved claim verification mechanisms
- Enhanced real-time notification system
- Production deployment setup
- REST API integration and a modern React-based frontend
- Advanced administrative permissions and reporting tools

---

## Changelog

All notable changes to this project will be documented in this section.

### [2.1.1] - Bug Fixes

#### Fixed
- Fixed an issue where item status was not displaying on item cards.
- Resolved a bug where filtering by lost or found status was not working correctly.

### [2.1.0] - Patch & Navigation Update

#### Added
- Added responsive design support across different screen sizes.
- Introduced an updated, better navbar and sidebar for improved navigation.

### [2.0.0] - UI Overhaul

#### Changed
- Completely redesigned the entire user interface with a modern look and feel.

### [1.0.0] - Initial Release

#### Added
- **Authentication System:** User registration, login, and logout functionality.
- **Student Dashboard:** Centralized dashboard to view personal posts, active claims, and claim status.
- **Item Reporting:** Ability to post lost or found items with title, description, campus location, item type, contact details, and image attachment.
- **Search & Filter:** Keyword search by item title and location, with filtering options for lost vs. found status.
- **Claim System:** Interactive workflow allowing users to submit claims on posted items.
- **Internal Notifications:** Automated internal system alerts notifying owners when a claim is placed on their item.
- **Claim Management:** Post owners can review pending claims and choose to accept or reject them.
- **Post Management:** Full CRUD capability for users to update or delete their listed items.
- **Admin Interface:** Integrated Django admin panel (`/admin/`) for overall database and user management.
- **Static & Media Asset Handling:** Configured WhiteNoise for static file serving and Pillow for media file management.

---

## Acknowledgements

UniFind was developed based on the open-source project
"CEC Lost & Found" by M Aswathy.

Original repository:
https://github.com/AswathyyM/lost_and_found_portal

The original project is licensed under the MIT License.
