from setuptools import setup

setup(
    name='twhousedetail',
    version='',
    packages=[''],
    url='https://github.com/tungyueh/tw-house-detail',
    license='',
    author='Tung-Yueh Lin',
    author_email='tungyuehlin@gmail.com',
    description='',
    install_requires=['selenium', 'beautifulsoup4'],
    entry_points={
        'console_scripts': ['house=twhousedetail.__main__:main']
    }
)
