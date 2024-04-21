from setuptools import setup, find_packages

# 패키지에 대한 설명
long_description = """
stock-lab is a Python package for stock analysis and visualization. 
It provides tools for downloading stock data, calculating various technical indicators, 
implementing trading strategies, and visualizing the results.
"""

setup(
    name='stock-lab',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'FinanceDataReader',
        'matplotlib',
        'plotly',
        'mplfinance',
    ],
    author='Ddangkwon',
    author_email='semi109502@gmail.com',
    description='A package for stock analysis and visualization',
    long_description=long_description,  # 설명 추가
    url='https://https://github.com/Ddangkwon/stock_lab/',
    keywords=['stocklab'],
    python_requires='>=3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],

)
