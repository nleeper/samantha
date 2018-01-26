# samantha
Personal assistant built to help you with all the things.

## Installation
Samantha uses Distutils for easy installation of the application. It is recommended to create a virtualenv to install the application in. To install Samantha, run the command:

`python setup.py install`

## Training
After installation is complete, you will want to train Samantha to respond to commands. There is an existing training file located at `data/training.json` with a reasonable amount of data, but you may want to add more to cover any of your use cases. 

To train Samantha and create the model, run the script:

`python tools/train.py`

If you make changes to the training data, you can train the model at any time by running this script again.

### Validating the model
After training, you will likely want to validate the model and run some sample commands against Samantha. To run commands against Samantha, run the script:

`python tools/parse.py`

You will be prompted to enter text, and you will be presented with the intent &entities that are parsed from the text. If an intent cannot be parsed with a minimum configured confidence level (by default 30%), then an error will be displayed with the full results of parsing.

## Running
To start Samantha listening, run the command:

`python server.py`

This will start Samantha listening on port 8888 by default.

## Configuration
Samantha has a few options that can be configured, and has some values that are required to use certain features like Facebook and Spotify.

## Rosie Integration
To use some of the commands Samantha is capable of, you will need to run an instance of Rosie inside of your home network. Rosie allows Samantha to control devices only accessible to your home network, like Sonos, Wemo or Nest products.

Rosie can be downloaded at:

[https://github.com/nleeper/rosie](https://github.com/nleeper/rosie)

## Development
If you want to develop on Samantha, after creating a virtualenv, run the command: 

`python setup.py develop`

This will allow you to make changes to the source code without needing to run `python setup.py install` after each change.

## Tests
To run tests on the project, run the command:

`python setup.py test`