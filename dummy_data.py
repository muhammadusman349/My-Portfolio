import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

import random
from faker import Faker
from django.contrib.auth import get_user_model
from portfolio.models import Project, ProjectComment, Skill, Education, Experience, Contact

fake = Faker()


def dummy_data():
    User = get_user_model()
    superusers = User.objects.filter(is_superuser=True)

    if not superusers.exists():
        print("No superuser found. Please create a superuser before running this script.")
        return

    owner = superusers.first()
    users = User.objects.filter(is_superuser=False)
    user = users.first()

    # Create skills
    print("Creating Skills...")
    skills = []
    for _ in range(10):
        skill = Skill.objects.create(
            user=owner,
            name=fake.job(),
            proficiency=random.randint(1, 5)
        )
        skills.append(skill)

    # Create projects
    print("Creating Projects...")
    projects = []
    for _ in range(5):
        project = Project.objects.create(
            user=owner,
            title=fake.sentence(),
            description=fake.paragraph(),
            technologies=", ".join([fake.word() for _ in range(3)]),
            github_link=fake.url(),
            live_link=fake.url(),
        )
        projects.append(project)

    # # Add comments and nested replies
    print("Creating Comments...")
    projects_ids = [11, 12, 13]
    projects = Project.objects.filter(id__in=projects_ids)
    for project in projects:
        for _ in range(random.randint(2, 5)):
            user_comment = ProjectComment.objects.create(
                project=project,
                user=user,
                text=fake.sentence(),
                status="approved"
            )
            for _ in range(random.randint(1, 3)):
                ProjectComment.objects.create(
                    project=project,
                    user=owner,
                    text=fake.sentence(),
                    parent_comment=user_comment,
                    status="approved"
                )

    # # Add education
    print("Creating Education...")
    for _ in range(5):
        Education.objects.create(
            user=owner,
            institution=fake.company(),
            degree=fake.job(),
            field_of_study=fake.word(),
            start_date=fake.date_between(start_date='-5y', end_date='-2y'),
            end_date=fake.date_between(start_date='-2y', end_date='today'),
            description=fake.paragraph()
        )

    # # Add experience
    print("Creating Experience...")
    for _ in range(5):
        experience = Experience.objects.create(
            user=owner,
            company=fake.company(),
            position=fake.job(),
            employment_type=random.choice(['FT', 'PT', 'CT', 'FE', 'IN']),
            location=fake.city(),
            start_date=fake.date_between(start_date='-10y', end_date='-5y'),
            description=fake.paragraph()
        )
        experience.technologies_used.add(*random.sample(skills, k=3))

    # # Add contact messages
    print("Creating Contact Messages...")
    for _ in range(10):
        Contact.objects.create(
            name=fake.name(),
            email=fake.email(),
            subject=fake.sentence(),
            message=fake.paragraph(),
            is_read=random.choice([True, False])
        )

    print("Demo data populated successfully.")


dummy_data()
