# Angel's Plant Shop

A Django-based e-commerce platform for selling plants and gardening supplies.

## Features

- User authentication and profile management
- Product catalog with categories
- Shopping cart functionality
- Checkout process
- Responsive design using Bootstrap 5

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd angels_plant
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://127.0.0.1:8000/ in your browser

## Project Structure

- `core/`: Main app with home page and user authentication
- `products/`: Product catalog and management
- `cart/`: Shopping cart functionality
- `checkout/`: Order processing and checkout

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. 