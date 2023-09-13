# Library API Service 

The Library API Service is a Django REST framework-based project designed to manage the system of tracking books, borrowings, users. This API allows you to retrieve information about books available in the library and make its borrowing till some date.

## Features

* Book information: Give information about books available in the library. System checks their availability using inventory field.

* Borrowing information: Allow users to create borrowing of the book, retrieve information about their borrowings, filter list of borrowings by active status (book returned or not), return book. Admin user can receive list of all borrowings and filter it to receive borrowings of specific user.
 
* Notification: After successful borrowing creation user receives message to Telegram chat about its details. 

* Authentication: User can create profile entering email and password. API is secured with JWT (JSON Web Tokens) authentication to protect sensitive data. 

## Getting Started
### Prerequisites
Before you begin, ensure you have met the following requirements:

- **Python**: Make sure you have Python 3.x installed on your system.

- **Pip**: Pip should be installed. Pip is a package manager for Python. You can check if you have it installed by running pip --version.

### Installation
Clone the repository:

```shell
git clone https://github.com/OksanaAdamchuk/library-service-api.git
cd library-service-api
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

- Create a .env file in the project root directory and set your configuration variables

- Migrate the database:
```shell
python manage.py migrate
```

- Create a superuser account:
```shell
python manage.py createsuperuser
```

- Start the development server:
```shell
python manage.py runserver
```
The API should now be accessible at http://localhost:8000/.

## Usage
### Authentication
To access certain endpoints, you need to authenticate your requests using JWT (JSON Web Tokens). You can obtain a token by registering a user account through the Django API and use the token endpoint to obtain a token.

To authenticate, include the obtained token in your request headers with the format:

```makefile
Authorize: Bearer <your-token>
```

### API Documentation
You can interact with the API using Swagger, a user-friendly API documentation tool. To access Swagger, open a web browser and navigate to http://localhost:8000/api/doc/swagger/. Here, you will find detailed information about the available endpoints and how to use them.

### Endpoints
The API provides the following endpoints:

Books Service:
* POST: api/books/ - add new book
* GET: api/books/ - get a list of books
* GET: api/books/<id>/ - get book's detail info 
* PUT/PATCH: api/books/<id>/ - update book
* DELETE: api/books/<id>/ - delete book

Users Service:

* POST: api/users/ - register a new user 
* POST: api/users/token/ - get JWT tokens 
* POST: api/users/token/refresh/ - refresh JWT token 
* GET: api/users/me/ - get my profile info 
* PUT/PATCH: api/users/me/ - update profile info

Borrowings Service:

* POST: api/borrowings/ - add new borrowing
* GET: api/borrowings/?user_id=...&is_active=... - get borrowings by user id and whether is borrowing still active or not.
* GET: api/borrowings/<id>/ - get specific borrowing 
* POST: api/borrowings/<id>/return/ - set actual return date
