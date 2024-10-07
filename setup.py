from setuptools import setup, find_packages

setup(
    name='wechat_scraping',  # Replace with your desired package name
    version='0.1.0',  # Initial version number
    description='A package for scraping WeChat Official Account posts data using a host and VirtualBox environment.',
    author='Ziyu He',  # Replace with your name
    author_email='zih028@ucsd.edu',  # Replace with your email
    url='https://github.com/harryziyuhe/wechat_scraping',  # Replace with your GitHub repository URL
    packages=find_packages(where='src'),  # Automatically find packages in 'src'
    package_dir={'': 'src'},  # Specify that packages are under 'src'
    include_package_data=True,  # Include data files specified in MANIFEST.in
    install_requires=[
        'pyautogui',        # For GUI automation
        'requests',         # For HTTP requests
        'stem',             # For controlling Tor
        'pandas',           # For data manipulation
        'urllib3',          # For advanced HTTP client capabilities
        'bs4',              # BeautifulSoup for parsing HTML
        'mitmproxy',        # For intercepting HTTP/HTTPS traffic
        'json',             # JSON library for parsing and generation (builtin in Python, usually not required in install_requires)
    ],
    entry_points={
        'console_scripts': [
            'wechat-scraper=wechat_scraper.host.wechat_scraper:main',  # Entry point for wechat_scraper on host
            'setup-vm=setup.setup_virtualbox_and_vm:main',  # Entry point for running the setup script
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Replace with your license if different
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Specify the minimum Python version required
)
