from setuptools import find_packages, setup
setup(
    name='backend-db-lib',
    packages=find_packages("app"),
    version='0.1.0',
    description='Backend Database Library',
    author='Backend-Gang',
    license='MIT',
    test_suite="tests",
)