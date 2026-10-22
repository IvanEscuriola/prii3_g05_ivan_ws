from setuptools import find_packages, setup
from glob import glob

package_name = 'g05_prii3_move_turtlebot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	('share/' + package_name + '/launch', glob('launch/*.launch.py')),
	('share/' + package_name + '/models', glob('models/*.sdf')),
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
		'draw_number = g05_prii3_move_turtlebot.draw_number:main',
		'laser_filter = g05_prii3_move_turtlebot.laser_filter:main',
		'evitar_colision = g05_prii3_move_turtlebot.evitar_colision:main',
		'collision_avoidance = g05_prii3_move_turtlebot.collision_avoidance:main',
		'obstacle_avoidance = g05_prii3_move_turtlebot.obstacle_avoidance:main',
        ],
    },
)
