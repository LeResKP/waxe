import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    # 'pyramid_auth',
    'zope.sqlalchemy',
    'waitress',
    'sqla_declarative',
    'xmltool',
]

setup(name='waxe',
      version='0.0',
      description='waxe',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='waxe',
      install_requires=requires,
      tests_require=[
          'nose',
          'nose-cov',
          'WebTest',
          'mock',
      ],
      entry_points="""\
      [paste.app_factory]
      main = waxe:main
      [console_scripts]
      initialize_waxe_db = waxe.scripts.initializedb:main
      """,
      )

