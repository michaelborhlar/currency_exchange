# 🌍 Country Currency & Exchange API
A Django RESTful API that fetches and stores country data from the REST Countries API, computes estimated GDP using real-time exchange rates from open.er-api.com, and provides CRUD endpoints to manage countries and track data refresh status. Built as part of the ALX Backend Engineering task and deployed on Railway.

## 🚀 Features
- Fetch and store country data (name, capital, region, population, flag, and currency).
- Compute estimated GDP using real-time exchange rates.
- CRUD operations for managing countries.
- Auto-refresh endpoint to sync data from external APIs.
- Tracks last refresh status and total countries stored.
- Fully deployed on Railway.

## 🧠 Technologies Used
- Python 3.13+
- Django 5+
- Django REST Framework
- MySQL (Railway-hosted)
- Requests (for API calls)
- Open Exchange Rate API
- REST Countries API

## ⚙️ Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/currency_exchange.git
   cd currency_exchange
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # (Windows)
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   DATABASE_URL=your_local_or_railway_database_url
   ```
5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Start the server:
   ```bash
   python manage.py runserver
   ```
7. Visit the API in your browser:
   [http://127.0.0.1:8000/api/countries/](http://127.0.0.1:8000/api/countries/)

## 🧩 API Endpoints
| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/countries/` | GET | List all countries |
| `/api/countries/name/` | GET | Retrieve a single country |
| `/api/countries/` | POST | Add a new country |
| `/api/countries/name/` | PUT/PATCH | Update a country |
| `/api/countries/name/` | DELETE | Delete a country |
| `/api/refresh/` | POST | Fetch and update all countries from external APIs |
| `/api/status/` | GET | Check last refresh status |

## 🌐 Deployment
Deployed on Railway:  
👉 [https://currencyexchange-production-3f95.up.railway.app](https://currencyexchange-production-3f95.up.railway.app)

## 👨‍💻 Author
**Michael Adefehinti**  
Backend Developer | ALX Backend Engineering Program  
📧 Email: michealadefehinti09@gmail.com  
🔗 GitHub: [https://github.com/mhykeborhlar](https://github.com/mhykeborhlar)
