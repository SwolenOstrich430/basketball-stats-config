import setuptools

setuptools.setup(
    name="basketball_stats_config",
    version="0.1.0",
    author="Peter Connelly",
    author_email="pconnelly898@gmail.com",
    license="MIT",
    description="Common config provider for all basketball-stats related repos",
    long_description="boop",
    long_description_content_type="text/markdown",
    url="https://github.com/SwolenOstrich430/basketball_reference_client",
    packages=setuptools.find_packages(),
    package_data={'bball_reference_client': ['*.txt']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'blinker',
        'click',
        'iniconfig',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'packaging',
        'pluggy',
        'Pygments',
        'Werkzeug'
    ],
    extras_require={
        'test': ['pytest', 'pytest-mock'],
    },
    keywords=[
        "nba",
        "sports",
        "data mining",
        "basketball",
        "basketball reference",
        "basketball-reference.com",
        ],
)