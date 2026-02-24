from setuptools import setup, find_packages

requires = [
    'SQLAlchemy>=2.0.0',
    'alembic>=1.13.0',
    'pyramid>=2.0.0',
    'pyramid_debugtoolbar>=4.11.0',
    'graphene>=3.0.0',
    'graphene-sqlalchemy>=3.0.0',
    'python-dateutil>=2.8.0',
    'python-dotenv>=1.0.0',
]

setup(
    name='web_is_vue_backend',
    version='0.1.0',
    description='Backend для личной CRM системы',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = backend:main',
        ],
        'console_scripts': [
            'initialize_web_is_vue_db = backend.scripts.initialize_db:main',
        ],
    },
)