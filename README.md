<!-- TODO Documentation:

* routes.py
* camera.py
* static/
* templates/ -->

# Nest Server (v2)

![Image of Nest Logo](https://i.imgur.com/wk2ynOg.jpg)

## Nest: Mobile Drone Port Client Server Application

An app from the IMPRESS Lab at Mississippi State University

[Our Site](http://impress.ece.msstate.edu/research/projects/Nest) ·
[View Demo](todo) ·
[Report Bug](https://github.com/lpjune/NestServerV2/issues) ·
[Request Feature](https://github.com/lpjune/NestServerV2/issues)

## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Docs](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [Contact](#contact)

<!-- ABOUT THE PROJECT -->
## About The Project

This is an application for the IMPRESS Labs.

We are developing a drone Nest for fully autonomous operations (no human intervention). Two drones can autonomously take off and land simultaneously, and their batteries are replaced by a robotic arm. The Nest is solar powered so it is self sustainable. Users can load pre-planned missions and the Nest allows collection of consistent repeatable data. With battery replacement by the robotic arm, drones are almost constantly available. The Nest also serves as data storage and connectivity during remote operations. It also includes several sensors and weather station for constant monitoring itself and environment around it.

The application will:

* Display video feed of the Nest
* Control the mechanical aspects of the Nest
* Keep a log of commands and errors
* Display visualization of the drone
* Act as a server to allow multiple clients to connect to the Nest

### Built With

* [Python 3.7.4](https://www.python.org/downloads/release/python-374/)
* [Flask](https://www.fullstackpython.com/flask.html) - This creates the video server
* [PyQt5](https://pypi.org/project/PyQt5/) - This is used to create the user interface
* [Selenium](https://selenium-python.readthedocs.io/) - This is used to communicate with the PLC
* [Matplotlib](https://matplotlib.org/users/installing.html) - This creates the drone landing plot in ```pad_plot.py``` 
* [Pillow](https://pypi.org/project/Pillow/) - This is used to store the drone landing image as a ```.jpg``` image.

<!-- GETTING STARTED -->
## Getting Started

Here are the instructions for setting up the app locally.

### Prerequisites

* Python 3.7+ installed with the following libraries
  * Flask
  * PyQt5 with QtWebEngineWidgets
  * Selenium
  * Cv2 (Open CV)
  * Pillow

To install these dependencies, run the following commands:

```bash
# Install in one line

pip3 install Flask PyQt5 PyQtWebEngine selenium opencv-python Pillow

# Or seperately

pip install Flask
pip install PyQt5
pip install PyQtWebEngine
pip install selenium
pip install opencv-python
pip install Pillow
```

### Installation

1. Clone the repo

    ```bash
    git clone https://github.com/impress-msu/NestApp.git
    ```

2. Modify the following strings in [StringConstants.py](StringConstants.py)

    ```python
    # Server configuration variables, these should match your machine
    SERVER_IP_ADDRESS = "192.168.0.6"
    SERVER_PORT = 8000

    ...
    # Direct path of chromedriver which can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/ 
    CHROMEDRIVERLOCATION = '/Users/laure/chromedriver'
    PLCURL = 'http://192.168.99.3/'
    ```

3. Open repo in prefered Python editor

4. Build and run the app
  
    ```bash
    python app.py
    ```

5. Build and run the client

    ```bash
    python app.py
    ```

## Docs

_For more info, please refer to the [Documentation](https://example.com)_

## Roadmap

See the [open issues](https://github.com/lpjune/NestServerV2/issues) for a list of proposed features (and known issues).

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

IMPRESS Lab - [@impress_lab](https://twitter.com/impress_lab) - email@example.com

Project Link: [https://github.com/impress-msu/NestApp](https://github.com/impress-msu/NestApp)