# Social Media App - Backend (In Development 🚧)

The backend of the Social Media App is built using Django and Django REST Framework, providing a robust and scalable API for the frontend. This project is actively being developed and new features are being added regularly.

## 🌟 Key Features (Current & Planned)

- ✅ **User Authentication**: JWT (JSON Web Tokens) for secure authentication
- ✅ **Friend System**: Send, accept, and reject friend requests
- ✅ **Real-time Notifications**: Using Django Channels and WebSockets
- ✅ **RESTful API**: Comprehensive API for frontend interactions
- ✅ **Real-time User Activity Status**: Online/Offline status 
- 🚧 **Chat System**: Real-time messaging (In Progress)
- 🔜 **User Groups**: Create and manage user groups (Planned)
- 🔜 **Media Sharing**: Share images and files (Planned)
- 🔜 **User Profile**: Extended user profiles (Planned)

## 🛠 Technologies Used

- **Django**: Web framework for rapid development
- **Django REST Framework**: Building Web APIs
- **Django Channels**: WebSocket support
- **Redis**: Message broker for WebSocket
- **PostgreSQL**: Database system
- **JWT**: Authentication mechanism

## 📁 Project Structure

The project structure is organized as follows:

- **backend/**
  - **chat/**                  - Real-time chat functionality (In Development)
  - **notifications/**         - Notification system
  - **users/**                 - User management
  - **friends/**               - Friend system
  - **websockets/**            - WebSocket handlers
  - **settings.py**            - Django configuration
  - **urls.py**                - URL routing
  - **wsgi.py**                - WSGI configuration

## 🔌 API Documentation

### Complete API Documentation
For detailed API documentation, visit:
- `/api/redoc/` - ReDoc API documentation
- `/api/swagger/` - Swagger UI documentation

### Key Endpoints

#### Authentication
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token

#### User Management
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - User details
- `PUT /api/users/{id}/` - Update profile

#### Friend System
- `POST /api/friends/request/` - Send request
- `PUT /api/friends/request/{id}/` - Accept/reject
- `GET /api/friends/` - List friends

#### Notifications
- `GET /api/notifications/` - List notifications
- `PUT /api/notifications/{id}/read/` - Mark as read
- `DELETE /api/notifications/{id}/` - Delete

## 🔌 WebSocket Connections

WebSocket endpoint for real-time features:


### Available WebSocket Events:
- `notification` - Real-time notifications
- `friend_request` - Friend request updates
- `online_status` - User online status (Coming Soon)
- `chat_message` - Real-time chat messages (Coming Soon)

## 🗄️ Database Schema

Currently implemented models:
- **User**: Core user data
- **FriendRequest**: Friend request management
- **Notification**: System notifications

Coming soon:
- **ChatRoom**: Group chat functionality
- **Message**: Private messaging
- **UserProfile**: Extended user profiles


### Database Schema
The application utilizes SQLite for data storage. The primary models include:

- **User**: Represents a user in the system, encompassing fields for username, email, and password.
- **FriendRequest**: Represents a friend request between users, including fields for sender, receiver, and status.
- **Notification**: Represents notifications sent to users, including fields for recipient, sender, text, and type.
- **More models in future**

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Redis
- PostgreSQL

## Installation

1. Clone the repository

### Running the Backend

To run the backend, ensure you have Python and the necessary packages installed. Use the following commands:

#### Navigate to the backend directory

`cd backend`

#### Create virtual environment

`python -m venv venv`

### Activate virtual environment

#### On Windows
`venv\Scripts\activate`

#### On Linux/Mac
`source venv/bin/activate`

### Install dependencies

`pip install -r requirements.txt`

### Run migrations

`python manage.py migrate`

### Start the development server

`python manage.py runserver`


## 📝 Development Status

This project is in active development. New features and improvements are being added regularly. Check the GitHub repository for the latest updates and planned features.

### Coming Soon
- Enhanced chat functionality
- File sharing capabilities
- User groups and permissions
- Advanced notification settings
- Message read receipts

## 🤝 Contributing

This project is open for contributions. Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License.

---
⚠️ Note: This is a development version. Features and endpoints may change as the project evolves.
