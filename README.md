<!-- TODO Documentation:

* routes.py
* camera.py
* static/
* templates/ -->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

# Nest Server (v2)

[![Total alerts](https://img.shields.io/lgtm/alerts/g/lpjune/Nest.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/lpjune/Nest/alerts/)

![shields.io](https://img.shields.io/github/repo-size/lpjune/nest.svg?style=popout)

<!-- PROJECT LOGO -->
</br>

<p align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://i.imgur.com/wk2ynOg.jpg" alt="Logo">
  </a>

  <h3 align="center">Nest: Mobile Drone Port Client Server Application</h3>
  <h4 align="center" style="margin-top:0">droNE_STation</h4>

  <p align="center">
    An app from the IMPRESS Lab at Mississippi State University
    </br>
    <a href="http://impress.ece.msstate.edu/research/projects/nest/"><strong>Our site »</strong></a>
    </br>
    </br>
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
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

This is an application for the IMPRESS Labs done nest.

We are developing a drone nest for fully autonomous operations (no human intervention). Two drones can autonomously take off and land simultaneously, and their batteries are replaced by a robotic arm. The NEST is solar powered so it is self sustainable. Users can load pre-planned missions and the NEST allows collection of consistent repeatable data. With battery replacement by the robotic arm, drones are almost constantly available. The NEST also serves as data storage and connectivity during remote operations. It also includes several sensors and weather station for constant monitoring itself and environment around it.

The application will:

* Display video feed of the nest
* Control the mechanical aspects of the nest
* Keep a log of commands and errors
* Display visualization of the drone
* Act as a server to allow multiple clients to connect to the nest

### Built With

* [Python 3.7.4](https://www.python.org/downloads/release/python-374/)
* [Flask](https://www.fullstackpython.com/flask.html)

<!-- GETTING STARTED -->
## Getting Started

Here are the instructions for setting up the app locally.

### Prerequisites

* Python 3.7+ installed with the following libraries
  * Flask
  * PyQt5 with QtWebEngineWidgets
  * Selenium
  * Cv2 (Open CV)

### Installation

1. Clone the repo

    ```sh
    git clone https://github.com/impress-msu/NestApp.git
    ```

2. Open repo in prefered Python editor
3. Build the app and run on device or virtual device

## Docs

_For more info, please refer to the [Documentation](https://example.com)_

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/lpjune/NestServerV2/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- CONTACT -->
## Contact

IMPRESS Lab - [@impress_lab](https://twitter.com/impress_lab) - email@example.com

Project Link: [https://github.com/impress-msu/NestApp](https://github.com/impress-msu/NestApp)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=flat-square
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=flat-square
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=flat-square
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=flat-square
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png