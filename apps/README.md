🍔 UrbanPlate Backend

The high-performance, asynchronous backend for the UrbanPlate food delivery application. Built with FastAPI, SQLAlchemy, and WebSockets.

🚀 Features
👤 Authentication & Users

JWT Auth: Secure login/registration with hashed passwords.

Role-Based Access: Distinction between customer, restaurant (admin), and admin.

Profile Management: Update email, password, and username safely.

Location Services: Store and update user delivery coordinates (Lat/Long) and address text.

🍕 Restaurant Management (Multi-Vendor)

Create Restaurant: Restaurant owners can register and create their own shops.

Menu System: Owners can Add, Edit, and Delete menu items (dishes).

Status Control: Open/Close restaurant status.

Security: Only the specific owner can edit their restaurant or menu.

📦 Orders & Real-Time Tracking

Place Order: Secure ordering linked to the logged-in user.

Background Tasks: Simulates kitchen workflow (Pending -> Cooking -> Ready).

Order History: Users can view their past orders.

💬 Live Order Chat

WebSockets: Real-time chat between Customer and Restaurant for active orders.

Hybrid Sync: Supports both WebSocket sending and HTTP POST fallback.

Auto-Wipe: Chat history is automatically deleted when the order is "Delivered" or "Cancelled" for privacy.

🛠️ Tech Stack

Framework: FastAPI (Python)

Database: SQLite (with SQLAlchemy ORM)

Real-Time: WebSockets

Validation: Pydantic Schemas

Security: OAuth2 with Password hashing (Bcrypt) + JWT

⚙️ Installation & Setup
1. Clone & Environment
code
Bash
download
content_copy
expand_less
# Clone the repository
git clone https://github.com/yourusername/urbanplate-backend.git
cd urbanplate-backend

# Create Virtual Environment
python -m venv .venv

# Activate Environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
2. Install Dependencies
code
Bash
download
content_copy
expand_less
pip install fastapi uvicorn sqlalchemy pydantic "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
3. Run the Server
code
Bash
download
content_copy
expand_less
# Note: The app is located in the 'apps' package
uvicorn apps.main:app --reload

The server will start at http://127.0.0.1:8000.

📖 API Documentation

FastAPI provides automatic interactive documentation.

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Key Endpoints
Method	Endpoint	Description
POST	/users/register	Register new user (Role: customer/restaurant)
POST	/users/login	Get Access Token (JWT)
POST	/restaurants/	Create a new Restaurant (Requires 'restaurant' role)
POST	/orders/place	Place a new food order
WS	/chat/ws/{id}/user	Connect to live chat for a specific order
📂 Project Structure
code
Text
download
content_copy
expand_less
urban_plate_backend/
├── urbanplate.db          # SQL Database file (Auto-created)
├── .venv/                 # Virtual Environment
├── apps/                  # Main Application Package
│   ├── main.py            # Entry Point
│   ├── models.py          # Database Tables
│   ├── database.py        # DB Connection
│   ├── auth.py            # Security & JWT Logic
│   ├── schemas/           # Pydantic Models (Validation)
│   │   ├── users.py
│   │   ├── restaurants.py
│   │   ├── orders.py
│   │   ├── chat.py
│   │   └── ...
│   └── routers/           # API Endpoints
│       ├── users.py
│       ├── restaurants.py
│       ├── orders.py
│       └── chat.py
🔮 Future Roadmap (API V2)

Search & Filtering for Restaurants.

Image Uploads for Menu Items.

Stripe/Khalti Payment Integration.

Push Notifications (FCM).