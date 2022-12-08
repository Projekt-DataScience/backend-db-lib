from setuptools import find_packages, setup
setup(
    name='backend_db_lib',
    packages=[ "backend_db_lib", "backend_db_lib.tests" ],
    version='0.1.0',
    description='Backend Database Library',
    author='Backend-Gang',
    license='MIT',
    test_suite="tests",
)
