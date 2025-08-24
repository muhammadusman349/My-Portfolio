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

## Key Features

### User Interface
- **Responsive Design**: Seamlessly adapts to all devices and screen sizes
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Modern UI Elements**:
  - Smooth transitions
  - Interactive project cards
  - Experience timeline
  - Skill chips with colored icons

### Technical Features
- **Authentication System**:
  - Secure user registration and login
  - Social authentication (Google, GitHub) via django-allauth
  - Profile management

- **Content Management**:
  - Projects
  - Experience
  - Education
  - Skills and technologies

- **Admin Dashboard**:
  - Custom dashboard UI
  - CRUD for portfolio content

### 🔧 Backend Features
- **Django Framework**
- **Database**:
  - SQLite by default (development)
  - PostgreSQL supported (optional)

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
- **SQLite** - Default development database
- **PostgreSQL** - Optional for production

### Frontend
- **HTML5** - Structure
- **Tailwind CSS (CDN)** - Styling
- **JavaScript** - Interactivity
- **jQuery** - Used in dashboard UI
- **Font Awesome** - Icons

#### Branding (Logo & Favicon)
- SVG logo mark: `static/logo/portfolio-logo-mark.svg`
- Site and Dashboard use the SVG as favicon via `<link rel="icon" type="image/svg+xml" href="{% static 'logo/portfolio-logo-mark.svg' %}">` in:
  - `templates/base.html`
  - `templates/dashboard/base.html`
- `/favicon.ico` is redirected to the SVG in `conf/urls.py`.

### Development Tools
- **Git** - Version control
- **VS Code** - IDE

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
│   ├── js/               # JavaScript files
│   └── logo/             # Branding assets (SVG favicon/logo)
├── media/                 # User uploads
├── requirements.txt       # Dependencies
└── manage.py             # Django CLI
```

## 🔐 Security Features

- Django's built-in protections (CSRF, XSS, SQL injection)
- Secure password hashing

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

## 🎨 Skill Icon Colors

- Bright, brand-consistent icon colors are applied via a Django template filter `skill_color` in `portfolio/templatetags/project_filters.py`.
- Used in `templates/portfolio/project_detail.html` and `templates/portfolio/experience_detail.html` on Font Awesome icons.
- Tailwind note: if you later add a Tailwind build step, safelist the dynamic classes returned by `skill_color` to avoid purging.

## 🔧 Configuration Snippets

- Favicon link (in `templates/base.html` and `templates/dashboard/base.html`):
  ```html
  <link rel="icon" type="image/svg+xml" href="{% static 'logo/portfolio-logo-mark.svg' %}">
  ```
- Favicon redirect (in `conf/urls.py`): `/favicon.ico` → `static/logo/portfolio-logo-mark.svg`

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
