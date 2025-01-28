## Overview of the Backend

The backend of the Social Media App is developed using Django and the Django REST Framework, offering a robust and scalable API for the frontend. It efficiently manages user authentication, friend requests, notifications, and real-time communication through WebSockets.

### Key Features

- **User Authentication**: Implements JWT (JSON Web Tokens) for secure user authentication and session management.
- **Friend System**: Enables users to send, accept, and reject friend requests while maintaining a list of friends.
- **Real-time Notifications**: Delivers notifications to users in real-time using Django Channels and WebSockets.
- **RESTful API**: Provides a comprehensive RESTful API for all frontend interactions, including user management, friend requests, and notifications.

### Technologies Utilized

- **Django**: A high-level Python web framework that promotes rapid development and clean, pragmatic design.
- **Django REST Framework**: A powerful toolkit for building Web APIs in Django, offering features such as serialization, authentication, and viewsets.
- **Django Channels**: Extends Django to support asynchronous protocols like WebSockets, enabling real-time functionalities.
- **Redis**: An in-memory data structure store used as a message broker for managing WebSocket connections and user sessions.
- **PostgreSQL**: A robust, open-source relational database system employed for storing user data, friend relationships, and notifications.

### Project Structure
backend/
├── chat/ # Functionality for chat
├── notifications/ # System for notifications
├── users/ # Management of users
├── friends/ # Handling of friend requests
├── websockets/ # Handlers for WebSocket connections
├── settings.py # Configuration settings for Django
├── urls.py # Routing of URLs
└── wsgi.py # WSGI entry point for the application

### API Endpoints

#### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Log in a user and obtain a JWT token
- `POST /api/auth/refresh/` - Refresh the JWT token

#### User Management
- `GET /api/users/` - Retrieve a list of users
- `GET /api/users/{id}/` - Get details of a specific user
- `PUT /api/users/{id}/` - Update user profile information

#### Friend System
- `POST /api/friends/request/` - Send a friend request
- `PUT /api/friends/request/{id}/` - Accept or reject a friend request
- `GET /api/friends/` - Retrieve a list of friends

#### Notifications
- `GET /api/notifications/` - Retrieve a list of notifications for the authenticated user
- `PUT /api/notifications/{id}/read/` - Mark a notification as read
- `DELETE /api/notifications/{id}/` - Delete a notification

For more endpoints, refer to /api/redoc

### WebSocket Implementation

The backend employs Django Channels to manage WebSocket connections for real-time notifications and status updates. The WebSocket endpoint is defined as follows:

ws://localhost:8000/ws/main/?token={jwt_token}

### Database Schema

The application utilizes PostgreSQL for data storage. The primary models include:

- **User**: Represents a user in the system, encompassing fields for username, email, and password.
- **FriendRequest**: Represents a friend request between users, including fields for sender, receiver, and status.
- **Notification**: Represents notifications sent to users, including fields for recipient, sender, text, and type.

### Running the Backend

To run the backend, ensure you have Python and the necessary packages installed. Use the following commands:

# Navigate to the backend directory

cd backend

Install dependencies

pip install -r requirements.txt

Run migrations
python manage.py migrate

Start the development server
python manage.py runserver

### Conclusion

The backend of the Social Media App is designed to be scalable, secure, and efficient, providing a solid foundation for the frontend application. With real-time capabilities and a comprehensive API, it enhances the user experience.

### Customization

Feel free to tailor this description based on your specific implementation details, such as:
- Any additional features you may have implemented
- Specific configurations or settings used in your Django project
- Any third-party libraries or tools that are part of your backend setup

This structure offers a clear overview of your backend, making it easier for others to understand its functionality and setup.
