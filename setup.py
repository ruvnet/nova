from setuptools import setup, find_packages

setup(
    name="conjecture",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'dspy-ai>=2.0.0',
        'pyyaml>=6.0',
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'python-dotenv>=0.19.0',
        'structlog>=21.1.0',
        'click>=8.0.0',
        'numpy>=1.21.0'
    ],
    entry_points={
        'console_scripts': [
            'cac=conjecture.cli:cli',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Cohen's Agentic Conjecture (CAC) Agent Implementation using DSPy",
    long_description=open('conjecture/docs/readme.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/conjecture",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
