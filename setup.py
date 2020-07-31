import setuptools

setuptools.setup(
    name="marlin",
    version="0.0.1",
    author="Andrea Benfatti",
    author_email="andrea.benfatti@univr.it",
    description="Intcatch marlin boat controller for raspberry pi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'gps==3.9',
        'Flask==1.0.2',
        'Flask-Classful==0.14.2',
        'singleton-decorator==1.0.0',
        'numpy==1.10.4',
        'simple_pid==0.1.4',
        'pyserial==3.4',
        'Adafruit-BNO055==1.0.2',
        'utm==0.4.2'
        ]
)

