import setuptools

with open('README.md', 'r') as infile:
    readme = infile.read()

setuptools.setup(
    name='iris-validation',
    version='0.2.1',
    author='William Rochira',
    author_email='william.rochira@hotmail.co.uk',
    maintainer='Ali Khan',
    maintainer_email='ak2535@york.ac.uk',
    description='A package for interactive all-in-one graphical validation of 3D protein model iterations',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    package_data={'iris_validation': [
        'metrics/percentiles/data/*',
        'metrics/rotamer/data/*',
        'graphics/js/*',]},
    include_package_data=True,
    url='https://github.com/glycojones/iris-validation',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent' ],
    python_requires='>=3',
    install_requires="svgwrite"
)
