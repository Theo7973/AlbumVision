from setuptools import setup, find_packages 
 
with open('requirements.txt') as f: 
    requirements = f.read().splitlines() 
 
setup( 
    name="AlbumVision", 
    version="0.1.0", 
    packages=find_packages(), 
    install_requires=requirements, 
    python_requires='
    author="Theo7973", 
    author_email="theo-soliman@outlook.com", 
    description="An image categorization and management application", 
) 
