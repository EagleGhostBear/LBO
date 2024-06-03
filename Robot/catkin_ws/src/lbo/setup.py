from setuptools import setup

package_name = 'lbo'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='SSAFY',
    maintainer_email='SSAFY@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom = lbo.odom:main',
            'make_map = lbo.make_map:main',
            'tt = lbo.tt:main',
            'lidar = lbo.lidar_test:main',
            'blue = lbo.bluetooth:main',
            'user = lbo.user_input:main',
            'camera_sub = lbo.camera_sub:main',
            'handle_odom = lbo.handle_odom:main',
            'handle_odom2 = lbo.handle_odom2:main',
            'tt_map = lbo.tt_map:main',
            'lidar_save = lbo.lidar_save:main',
        ],
    },
)
