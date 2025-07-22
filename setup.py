from setuptools import setup, find_packages

setup(
    name='iqoptionbot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
    ],
    include_package_data = True,
    package_data={'iqoptionbot':['config.txt', 'login.txt']},
    entry_points={
        'console_scripts': [
            'iqoptionbot=iqoptionbot.__main__:main',  # ajusta al nombre de tu función principal
        ],
    },
    author='Victor',
    description='Bot modular para IqOption con señales y gestión de riesgo',
    url='https://github.com/vhenriquezn/IqOptionBot',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
