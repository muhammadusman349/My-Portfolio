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
    """Return a FontAwesome class for a given skill name.

    Examples:
    - Python -> "fab fa-python"
    - JavaScript -> "fab fa-js"
    - Default -> "fas fa-code"
    """
    if not skill_name:
        return 'fas fa-code'

    name = str(skill_name).strip().lower()

    mapping = {
        'python': 'fab fa-python',
        'django': 'fas fa-leaf',  # no official FA brand, using leaf as a tasteful stand-in
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
        'nextjs': 'fab fa-react',
        'vue': 'fab fa-vuejs',
        'node': 'fab fa-node',
        'node.js': 'fab fa-node',
        'nodejs': 'fab fa-node',
        'express': 'fas fa-route',
        'postgresql': 'fas fa-database',
        'postgres': 'fas fa-database',
        'mysql': 'fas fa-database',
        'sqlite': 'fas fa-database',
        'mongodb': 'fas fa-database',
        'redis': 'fas fa-database',
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
        'redis': 'fas fa-database',
        'graphql': 'fas fa-project-diagram',
        'drf': 'fas fa-plug',
        'rest api': 'fas fa-plug',
        'jira': 'fab fa-jira',
        'webpack': 'fas fa-cubes',
        'vite': 'fas fa-bolt',
    }

    # try exact match
    if name in mapping:
        return mapping[name]

    # fuzzy contains checks for common keywords
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
        if key in name:
            return icon

    return 'fas fa-code'


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
