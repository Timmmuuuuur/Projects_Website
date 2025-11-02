# Timur's Portfolio - Django Web Application

A modern, beautiful portfolio website showcasing two computational tools: a Vehicle Routing Problem optimizer and a Graduate School Admission predictor.

## 🎨 Features

- **Modern UI/UX**: Beautiful gradient backgrounds, smooth animations, and responsive design
- **Vehicle Routing Optimizer**: Solves the NP-hard VRP using Tabu Search algorithm
- **Grad School Predictor**: ML-powered admission probability calculator using Logistic Regression
- **User Authentication**: Register, login, and logout functionality
- **Mobile Responsive**: Works perfectly on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Chrome/Chromium browser (for VRP web scraping)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd /Users/teimourdavletov/Desktop/djangoMigration
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt --user
   ```
   
   If you encounter SSL certificate errors on macOS:
   ```bash
   pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt --user
   ```

3. **Apply database migrations:**
   ```bash
   python3 manage.py migrate
   ```

4. **(Optional) Create a superuser for admin access:**
   ```bash
   python3 manage.py createsuperuser
   ```

### Running the Application

1. **Start the development server:**
   ```bash
   python3 manage.py runserver
   ```

2. **Open your browser and visit:**
   - Homepage: http://localhost:8000/
   - Vehicle Routing: http://localhost:8000/vrp/
   - Admission Predictor: http://localhost:8000/uni_admin/
   - Admin Panel: http://localhost:8000/admin/

3. **To stop the server:**
   - Press `Ctrl + C` in the terminal

## 📱 Pages

- **Homepage** (`/`): Portfolio introduction with featured projects
- **Vehicle Routing** (`/vrp/`): Optimize routes for multiple vehicles
- **Admission Predictor** (`/uni_admin/`): Calculate grad school admission probability
- **Register** (`/register/`): Create a new account
- **Login** (`/login/`): Sign in to your account
- **Admin Panel** (`/admin/`): Django admin interface

## 🛠️ Technologies Used

### Backend
- Django 3.0.6
- Python 3.x
- SQLite3

### Frontend
- Materialize CSS
- Custom CSS with modern design system
- Google Fonts (Inter)
- Material Icons

### Machine Learning & Algorithms
- scikit-learn (Logistic Regression)
- NumPy & Pandas
- Tabu Search Algorithm
- Haversine Formula

### Web Automation
- Selenium WebDriver

## 📊 Project Structure

```
djangoMigration/
├── main/                          # Main Django app
│   ├── models.py                  # Database models
│   ├── views.py                   # View functions
│   ├── forms.py                   # Form definitions
│   ├── urls.py                    # URL routing
│   ├── static/main/css/           # CSS files
│   │   ├── custom.css            # Modern custom styles
│   │   └── materialize.css       # Materialize framework
│   ├── templates/main/            # HTML templates
│   │   ├── header.html           # Base template
│   │   ├── home.html             # Homepage
│   │   ├── vrp.html              # VRP tool
│   │   ├── uni_admin.html        # Admission predictor
│   │   ├── login.html            # Login page
│   │   └── register.html         # Registration page
│   └── binary.csv                 # Training data for ML model
├── upgraded_django_test/          # Project settings
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI config
├── db.sqlite3                     # SQLite database
├── manage.py                      # Django management script
└── requirements.txt               # Python dependencies

```

## 🎯 Key Features Explained

### Vehicle Routing Problem Solver
- Uses Selenium to geocode addresses via web scraping
- Calculates distance matrix using Haversine formula
- Implements Tabu Search for route optimization
- Generates Google Maps URLs for visualizing routes

### Graduate School Admission Predictor
- Trained on 400+ real admission records
- Uses Logistic Regression for probability prediction
- Inputs: GRE score, GPA, institution rank
- Output: Admission probability percentage

## 🎨 Design System

The application features a modern design with:
- Purple-green gradient backgrounds
- Smooth animations and transitions
- Card-based layouts with hover effects
- Responsive grid system
- Modern typography (Inter font family)
- Intuitive color-coded notifications

## ⚠️ Notes

- The VRP solver requires an active internet connection for geocoding
- ChromeDriver must be installed for Selenium to work
- The ML model retrains on each request (consider caching for production)
- Debug mode is currently enabled (disable for production deployment)

## 👨‍💻 Author

**Timur Dauletov**
- Computer Engineering Student @ University of Waterloo
- Passionate about algorithms, ML, and web development

## 📝 License

This is a personal portfolio project.

---

**Enjoy exploring the projects! 🚀**

