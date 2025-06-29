from setuptools import setup, find_packages
import os
import sys

# Add the current directory to the path so vgdl can be imported
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

# Get the long description from the README file
long_description = ""
if os.path.exists(os.path.join(here, 'README.md')):
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

# Find all package data files
def find_package_data():
    package_data = {}
    
    # Include all files in vgdl package
    for root, dirs, files in os.walk('vgdl'):
        if files:
            package_name = 'vgdl_env.vgdl'
            if root != 'vgdl':
                rel_path = os.path.relpath(root, 'vgdl')
                package_name = f'vgdl_env.vgdl.{rel_path.replace(os.sep, ".")}'  
            package_data[package_name] = ['*.py', '*.pyc', '*.txt', '*.json', '*.dot', '*.png']
    
    # Include game files
    for root, dirs, files in os.walk('games'):
        if files:
            package_name = 'vgdl_env.games'
            if root != 'games':
                rel_path = os.path.relpath(root, 'games')
                package_name = f'vgdl_env.games.{rel_path.replace(os.sep, ".")}'
            package_data[package_name] = ['*.*']
    
    return package_data

setup(
    name="vgdl_env",
    version="0.1.0",
    description="VGDL (Video Game Definition Language) Python Environment",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Original: Tom Schaul, Modified for Python 3",
    url="https://github.com/yourusername/vgdl_env",
    packages=[
        'vgdl_env',
        'vgdl_env.vgdl',
        'vgdl_env.games',
    ] + [
        f'vgdl_env.vgdl.{d.replace(os.sep, ".")}'  
        for d, _, _ in os.walk('vgdl') if d != 'vgdl'
    ] + [
        f'vgdl_env.games.{d.replace(os.sep, ".")}'  
        for d, _, _ in os.walk('games') if d != 'games'
    ],
    package_dir={
        'vgdl_env': '.',  # The root directory is the vgdl_env package
    },
    package_data=find_package_data(),
    include_package_data=True,
    install_requires=[
        'numpy>=1.20.0,<2.0.0',
        'pygame>=2.0.0',
        'gym>=0.21.0',
        'gymnasium==0.29.1',
        'termcolor>=1.1.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    entry_points={
        'console_scripts': [
            'vgdl=vgdl.play:main',
        ],
    },
)
