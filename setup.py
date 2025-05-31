from setuptools import setup, find_packages

setup(
    name="military_packing_list",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Django>=5.2.1",
        "gunicorn>=20.1",
        "psycopg2-binary>=2.9",
    ],
) 