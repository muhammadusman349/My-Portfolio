from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter(name='skill_icon')
def skill_icon(skill_name: str) -> str:
    """Return a FontAwesome class for a given skill name."""

    if not skill_name:
        return 'fas fa-question-circle'

    skill_name = str(skill_name).strip().lower()

    # Testing and QA icons
    testing_icons = {
        # General Testing
        'testing': 'fas fa-vial',
        'qa': 'fas fa-check-double',
        'quality assurance': 'fas fa-check-double',
        'test automation': 'fas fa-robot',
        'manual testing': 'fas fa-hand-paper',
        'exploratory testing': 'fas fa-search',
        'ad-hoc testing': 'fas fa-lightbulb',
        'regression testing': 'fas fa-undo',
        'smoke testing': 'fas fa-smoking',
        'sanity testing': 'fas fa-brain',
        'ui testing': 'fas fa-desktop',
        'user interface testing': 'fas fa-desktop',
        'api testing': 'fas fa-plug',
        'acceptance testing': 'fas fa-clipboard-check',
        'functional testing': 'fas fa-tasks',
        'unit testing': 'fas fa-cube',
        'integration testing': 'fas fa-puzzle-piece',
        'system testing': 'fas fa-server',
        'end-to-end testing': 'fas fa-project-diagram',

        # Performance Testing
        'performance testing': 'fas fa-tachometer-alt',
        'load testing': 'fas fa-weight-hanging',
        'stress testing': 'fas fa-bolt',
        'scalability testing': 'fas fa-expand-arrows-alt',
        'volume testing': 'fas fa-database',
        'endurance testing': 'fas fa-hourglass-half',
        'soak testing': 'fas fa-hourglass-half',

        # Security Testing
        'security testing': 'fas fa-shield-alt',
        'penetration testing': 'fas fa-user-secret',

        # Other Testing Types
        'usability testing': 'fas fa-user-check',
        'compatibility testing': 'fas fa-mobile-alt',
        'reliability testing': 'fas fa-shield-virus',
        'maintainability testing': 'fas fa-tools',
        'portability testing': 'fas fa-laptop-code',
        'compliance testing': 'fas fa-file-contract',
        'localization testing': 'fas fa-language',
        'internationalization testing': 'fas fa-globe',
        'i18n testing': 'fas fa-globe',
        'l10n testing': 'fas fa-language',

        # Testing Tools
        'selenium': 'fas fa-window-maximize',
        'junit': 'fas fa-flask',
        'testng': 'fas fa-flask',
        'pytest': 'fas fa-flask',
        'cypress': 'fas fa-ghost',
        'postman': 'fas fa-paper-plane',
        'jmeter': 'fas fa-tachometer-alt',
        'loadrunner': 'fas fa-tachometer-alt',
    }

    # Exact match check
    if skill_name in testing_icons:
        return testing_icons[skill_name]

    # Partial match check
    for key, icon in testing_icons.items():
        if key in skill_name:
            return icon

    # Development / Tools
    if 'jupyter' in skill_name.lower():
        return 'fas fa-book'  # Represents Jupyter notebook
    if 'test case' in skill_name.lower() or 'test execution' in skill_name.lower():
        return 'fas fa-tasks'  # For test case design/execution
    if 'test planning' in skill_name.lower() or 'test strategy' in skill_name.lower():
        return 'fas fa-clipboard-check'  # For test planning/strategy
    if 'defect' in skill_name.lower() or 'life cycle' in skill_name.lower() or 'lifecycle' in skill_name.lower():
        return 'fas fa-bug'  # For defect lifecycle management
    if 'vs code' in skill_name or 'vscode' in skill_name or 'visual studio code' in skill_name:
        return 'devicon-vscode-plain colored'  # VS Code icon
    if 'html' in skill_name or 'html5' in skill_name or 'html 5' in skill_name.lower():
        return 'fab fa-html5'
    if 'npm' in skill_name:
        return 'fab fa-npm'
    if 'ubuntu' in skill_name:
        return 'fab fa-ubuntu'
    if 'pytorch' in skill_name:
        return 'fab fa-python'  # PyTorch is primarily Python-based
    if 'tensorflow' in skill_name:
        return 'fas fa-project-diagram'  # Represents the computational graph
    if 'machine learning' in skill_name or 'ml' in skill_name:
        return 'fas fa-brain'
    if 'ai' in skill_name or 'artificial intelligence' in skill_name:
        return 'fas fa-robot'
    if 'numpy' in skill_name:
        return 'fas fa-calculator'
    if 'bug' in skill_name or 'bug tracking' in skill_name:
        return 'fas fa-bug'
    if 'agile' in skill_name or 'scrum' in skill_name:
        return 'fas fa-tasks'
    if 'jenkins' in skill_name or 'ci/cd' in skill_name or 'continuous integration' in skill_name:
        return 'fab fa-jenkins'
    if "pandas" in skill_name.lower():
        return "devicon-pandas-plain colored"  # Official pandas icon from Devicon

    # Mapping for tech stack
    mapping = {
        'python': 'fab fa-python',
        'django': 'devicon-django-plain colored',
        'flask': 'fas fa-flask',
        'fastapi': 'fas fa-bolt',
        'javascript': 'fab fa-js',
        'typescript': 'fab fa-js',
        'html': 'fab fa-html5',
        'html5': 'fab fa-html5',
        'css': 'fab fa-css3-alt',
        'css3': 'fab fa-css3-alt',
        'tailwind': 'fas fa-wind',
        'bootstrap': 'fab fa-bootstrap',
        'react': 'fab fa-react',
        'next.js': 'fab fa-react',
        'vue': 'fab fa-vuejs',
        'node': 'fab fa-node',
        'express': 'fas fa-route',
        'postgresql': 'fas fa-database',
        'mysql': 'fas fa-database',
        'sqlite': 'fas fa-database',
        'mongodb': 'fas fa-database',
        'redis': 'devicon-redis-plain colored',
        'docker': 'fab fa-docker',
        'kubernetes': 'fas fa-cloud',
        'git': 'fab fa-git-alt',
        'github': 'fab fa-github',
        'gitlab': 'fab fa-gitlab',
        'aws': 'fab fa-aws',
        'azure': 'fab fa-microsoft',
        'gcp': 'fab fa-google',
        'linux': 'fab fa-linux',
        'nginx': 'fas fa-server',
        'gunicorn': 'fas fa-feather',
        'celery': 'fas fa-seedling',
        'rabbitmq': 'fas fa-envelope-open-text',
        'graphql': 'fas fa-project-diagram',
        'drf': 'fas fa-plug',
        'rest api': 'fas fa-plug',
        'jira': 'fab fa-jira',
        'webpack': 'fas fa-cubes',
        'vite': 'fas fa-bolt',
    }

    # Try exact
    if skill_name in mapping:
        return mapping[skill_name]

    # Fuzzy keyword check
    keywords = [
        ('python', 'fab fa-python'),
        ('django', 'fas fa-leaf'),
        ('react', 'fab fa-react'),
        ('vue', 'fab fa-vuejs'),
        ('node', 'fab fa-node'),
        ('js', 'fab fa-js'),
        ('html', 'fab fa-html5'),
        ('css', 'fab fa-css3-alt'),
        ('docker', 'fab fa-docker'),
        ('git', 'fab fa-git-alt'),
        ('aws', 'fab fa-aws'),
        ('linux', 'fab fa-linux'),
        ('sql', 'fas fa-database'),
        ('db', 'fas fa-database'),
    ]
    for key, icon in keywords:
        if key in skill_name:
            return icon

    # Default fallback
    return 'fas fa-question-circle'

@register.filter(name='skill_color')
def skill_color(skill_name: str) -> str:
    """Return Tailwind text color classes for a given skill to make icons bright.

    Examples:
    - Python -> "text-blue-600 dark:text-blue-400"
    - JavaScript -> "text-yellow-400"
    - Default -> "text-indigo-500 dark:text-indigo-400"
    """
    if not skill_name:
        return 'text-indigo-500 dark:text-indigo-400'

    name = str(skill_name).strip().lower()

    mapping = {
        'python': 'text-blue-600 dark:text-blue-400',
        'django': 'text-green-600 dark:text-green-400',
        'flask': 'text-emerald-600 dark:text-emerald-400',
        'fastapi': 'text-teal-500 dark:text-teal-400',
        'javascript': 'text-yellow-400',
        'typescript': 'text-blue-600 dark:text-blue-400',
        'react': 'text-sky-400',
        'next.js': 'text-sky-400',
        'nextjs': 'text-sky-400',
        'vue': 'text-green-500',
        'node': 'text-green-600',
        'node.js': 'text-green-600',
        'nodejs': 'text-green-600',
        'express': 'text-gray-600 dark:text-gray-300',
        'html': 'text-orange-500',
        'html5': 'text-orange-500',
        'css': 'text-blue-500',
        'css3': 'text-blue-500',
        'tailwind': 'text-cyan-500',
        'bootstrap': 'text-purple-600',
        'postgresql': 'text-blue-600',
        'postgres': 'text-blue-600',
        'mysql': 'text-blue-600',
        'sqlite': 'text-indigo-500',
        'mongodb': 'text-green-600',
        'redis': 'text-red-500',
        'docker': 'text-blue-500',
        'kubernetes': 'text-blue-600',
        'git': 'text-orange-600',
        'github': 'text-gray-800 dark:text-gray-200',
        'gitlab': 'text-orange-600',
        'aws': 'text-orange-500',
        'azure': 'text-blue-600',
        'gcp': 'text-red-500',
        'linux': 'text-gray-800 dark:text-gray-200',
        'nginx': 'text-emerald-600',
        'gunicorn': 'text-emerald-600',
        'celery': 'text-green-600',
        'graphql': 'text-pink-500',
        'drf': 'text-indigo-600',
        'rest api': 'text-indigo-600',
        'jira': 'text-blue-600',
        'webpack': 'text-blue-500',
        'vite': 'text-yellow-400',
    }

    if name in mapping:
        return mapping[name]

    # Keyword-based defaults
    keywords = [
        ('python', 'text-blue-600 dark:text-blue-400'),
        ('django', 'text-green-600 dark:text-green-400'),
        ('react', 'text-sky-400'),
        ('vue', 'text-green-500'),
        ('node', 'text-green-600'),
        ('js', 'text-yellow-400'),
        ('html', 'text-orange-500'),
        ('css', 'text-blue-500'),
        ('docker', 'text-blue-500'),
        ('git', 'text-orange-600'),
        ('aws', 'text-orange-500'),
        ('linux', 'text-gray-800 dark:text-gray-200'),
        ('sql', 'text-blue-600'),
        ('db', 'text-blue-600'),
    ]
    for key, color in keywords:
        if key in name:
            return color

    return 'text-indigo-500 dark:text-indigo-400'
