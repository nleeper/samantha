from setuptools import setup, find_packages
from setuptools.command.install import install

class DownloadSpacy(install):
    def run(self):
        install.do_egg_install(self)
        import spacy
        spacy.cli.download('download', 'en')

INSTALL_REQUIRES = [
    'rasa-nlu==0.10.6',
    'python-crfsuite==0.9.5',
    'numpy==1.14',
    'scipy==1.0.0',
    'spacy==2.0.5',
    'tornado==4.5.1',
    'spotipy==2.4.4',
    'scikit-learn==0.19.1',
    'python-decouple==3.1',
    'requests==2.16.0',
    'sklearn-crfsuite==0.3.6'
]

SETUP_REQUIRES = [
    'spacy==2.0.5',
    'pytest-runner'
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