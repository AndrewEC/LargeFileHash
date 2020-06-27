from setuptools import setup

if __name__ == '__main__':
    setup(
        name='largefilehash',
        version='1.0',
        description='Pseudo sha hasing for large files',
        author='Andrew Cumming',
        author_email='andrew.cumming@gmail.com',
        url='https://github.com/AndrewEC/largefilehash',
        packages=['largefilehash'],
        install_requires=[
            'coverage==5.0.3',
            'cosmic_ray==6.1.0',
            'virtualenv==16.7.9',
            'click==7.0'
        ]
    )
