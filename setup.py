from setuptools import setup, find_packages
from setuptools.command.install import install

def spacy_download_en():
    import subprocess
    args = ['python -m spacy download en']
    subprocess.call(args, shell=True)

class DownloadSpacy(install):
    def run(self):
        install.do_egg_install(self)
        spacy_download_en()
        install.run(self)

INSTALL_REQUIRES = [
    'rasa-nlu==0.8.9',
    'python-crfsuite==0.9.2',
    'numpy==1.12.1',
    'scipy==0.19.0',
    'spacy==1.8.2',
    'tornado==4.5.1',
    'spotipy==2.4.4',
    'scikit-learn==0.18.1',
    'python-decouple==3.1',
    'requests==2.16.0'
]

SETUP_REQUIRES = [
    'spacy==1.8.2'
]

TESTS_REQUIRE = [
    'pytest',
    'mock'
]

CMDCLASS = {
    'install': DownloadSpacy
}

setup(
    name='Samantha',
    version='0.1',
    description='Assistant to help you with whatever you need',
    author='Nick Leeper',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
    cmdclass=CMDCLASS
)