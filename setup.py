from setuptools import setup, find_packages

setup(
    name='cyber-attack-simulator',
    version='0.1.0',
    author="Atsu Vovor, MMA | Consultant, Data & Analytics",
    author_email="atsu.vovor@bell.net",
    description="Cyber attack simulation tool with Streamlit frontend and AI validation agent.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/atsuvovor/cyber-attack-simulator',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Streamlit',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'cyber-sim=cyber_attack_simulator.app:main'
        ],
    },
)
