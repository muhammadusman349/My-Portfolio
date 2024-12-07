# Modern Portfolio Website 🚀

A professional portfolio website showcasing my work, built with Django and modern web technologies. Features a sleek design with dark mode support, responsive layout, and dynamic content management.

## 📸 Screenshots

<div align="center">

### 🌟 Theme Modes
| Light Mode | Dark Mode |
|:----------:|:---------:|
| ![Light-Mode](assets/Screenshot%20(112).png) | ![Dark-Mode](assets/Screenshot%20(133).png) |

### 🎯 Main Portfolio Sections
| Home | Login | Projects |
|:----:|:-------------:|:--------:|
| ![Home](assets/Screenshot%20(112).png) | ![Login](assets/Screenshot%20(134).png) | ![Projects](assets/Screenshot%20(129).png) |

| Experience | Education | Skills |
|:----------:|:---------:|:------:|
| ![Experience](assets/Screenshot%20(130).png) | ![Education](assets/Screenshot%20(131).png) | ![Skills](assets/Screenshot%20(132).png) |

### 💼 Additional Features
| Dashboard | Project Details | Contact |
|:---------:|:--------------:|:-------:|
| ![Dashboard](assets/Screenshot%20(123).png) | ![Project-Details](assets/Screenshot%20(124).png) | ![Contact](assets/Screenshot%20(122).png) |

</div>

## ✨ Key Features

### 💫 User Interface
- **Responsive Design**: Seamlessly adapts to all devices and screen sizes
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Modern UI Elements**: 
  - Smooth animations and transitions
  - Interactive project cards
  - Dynamic timeline for experience
  - Skill progress visualization
  - Custom loading animations

### 🛠 Technical Features
- **Authentication System**:
  - Secure user registration and login
  - Social authentication integration
  - Password reset functionality
  - Login With Social Media (Google,Github)
  - Profile management

- **Content Management**:
  - Dynamic project portfolio
  - Experience timeline
  - Education history
  - Skills and technologies
  - Blog posts (Coming Soon)

- **Admin Dashboard**:
  - Custom admin interface
  - Content management system
  - User analytics
  - SEO optimization tools

### 🔧 Backend Features
- **Django Framework**:
  - MVT architecture
  - Custom user models
  - Advanced querysets
  - Middleware implementations

- **Database**:
  - Optimized database schema
  - Efficient queries
  - Data validation
  - Backup systems

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/muhammadusman349/Django-Portfolio_Website.git
cd Django-Portfolio_Website
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with the following:
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start development server:
```bash
python manage.py runserver
```

## 🛠️ Tech Stack

### Backend
- **Django** - Web framework
- **Python** - Programming language
- **PostgreSQL** - Database
- **Django REST Framework** - API development
- **Celery** - Task queue (Coming Soon)
- **Redis** - Caching (Coming Soon)

### Frontend
- **HTML5** - Structure
- **Tailwind CSS** - Styling
- **JavaScript** - Interactivity
- **Alpine.js** - Frontend framework
- **Font Awesome** - Icons
- **GSAP** - Animations (Coming Soon)

### Development Tools
- **Git** - Version control
- **VS Code** - IDE
- **Docker** - Containerization
- **Nginx** - Web server
- **Gunicorn** - WSGI server

## 📁 Project Structure

```
Django-Portfolio_Website/
├── accounts/                # User authentication
│   ├── models.py           # Custom user model
│   └── views.py            # Auth views
├── portfolio/              # Main portfolio app
│   ├── models.py           # Data models
│   └── views.py            # View logic
├── dashboard/              # Admin dashboard
│   └── views.py            # Dashboard views
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── portfolio/         # Portfolio templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── media/                 # User uploads
├── requirements.txt       # Dependencies
└── manage.py             # Django CLI
```

## 🔐 Security Features

- Django's built-in security
- CSRF protection
- XSS prevention
- SQL injection prevention
- Secure password hashing
- Rate limiting
- Session security
- HTTPS enforcement
- Security headers
- Input validation

<!-- ## 🚀 Deployment

1. Server Setup:
   - Ubuntu 20.04 LTS
   - Nginx configuration
   - SSL certificate
   - Domain configuration

2. Database Setup:
   - PostgreSQL installation
   - Database optimization
   - Backup configuration

3. Application Deployment:
   - Gunicorn setup
   - Static files serving
   - Media files handling
   - Environment variables

4. Monitoring:
   - Server monitoring
   - Error tracking
   - Performance metrics
   - Backup verification -->

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For any queries or suggestions, please reach out:
- **Email**: muhammadusman67200@gmail.com
- **LinkedIn**: [[LinkedIn](https://www.linkedin.com/in/muhammad-usman-profile/)]
- **GitHub**: [[GitHub](https://github.com/muhammadusman349)]
<!-- - **Portfolio**: [Your Portfolio URL] -->

## 🙏 Acknowledgments

- Django Documentation
- Tailwind CSS
- Font Awesome
- Alpine.js
- All contributors and supporters
