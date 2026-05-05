from setuptools import setup, find_packages

setup(
    name='ros2_helper',
    version='0.1.0',
    description='ROS2 话题扫描工具 - 支持QOS解析和消息内容解析',
    author='ROS2 Helper',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'pyyaml>=5.4',
        'pick>=2.0',
        'prompt-toolkit>=3.0',
    ],
    entry_points={
        'console_scripts': [
            'ros2-helper=ros2_helper.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
