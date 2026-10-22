from setuptools import find_packages, setup
from glob import glob

package_name = 'g05_prii3_move_jetbot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	('share/' + pcakage_name + '/launch', glob('launch/*.launch.py'),),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ivanubnt',
    maintainer_email='xivanxesc6@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'draw_number = g05_prii3_move_jetbot.draw_number:main',
        ],
    },
)
