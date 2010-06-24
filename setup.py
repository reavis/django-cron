from setuptools import setup, find_packages

setup(name="django-cron",
           version="0.1",
           description="Django application automating tasks.",
           author="Reavis Sutphin-Gray",
           author_email="reavis-django-cron@sutphin-gray.com",
           packages=find_packages(),
           include_package_data=True,
)