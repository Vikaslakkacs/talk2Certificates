from setuptools import find_packages, setup

setup (
    name='talk2certificates',
    vesion= '0.0.1',
    author='vikaslakkacs@gmail.com',
    author_email='vikaslakkacs@gmail.com',
    install_requires= ['openai', 'langchain', 'streamlit', 'python-dotenv', 'PyPDF2'],
    packages= find_packages(where="src"),
    package_dir={"":"src"}
)