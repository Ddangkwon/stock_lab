from setuptools import setup, find_packages

setup(
    name='stock-lab',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'FinanceDataReader',
        'matplotlib',
        'plotly',
    ],
    author='Ddangkwon',
    author_email='semi109502@gmail.com',
    description='A package for stock analysis and visualization',
    url='https://https://github.com/Ddangkwon/stock_lab/',
)