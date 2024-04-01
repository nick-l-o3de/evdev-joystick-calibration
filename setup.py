from setuptools import setup, find_packages

setup(
    name='evdev-joystick-calibration',
    version='0.1.1',
    description='Run, pick up the gamepad and turn sticks with triggers around',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nick-l-o3de/evdev-joystick-calibration',
    author='Nicholas Lawson',
    author_email='70027408+nick-l-o3de@users.noreply.github.com',
    license='MIT',
    install_requires=['evdev>=1.3.0'],
    packages=find_packages(),
    entry_points=dict(
        console_scripts=['evdev-joystick-calibration=evdev_joystick_calibration.__main__:main']
    )
)
