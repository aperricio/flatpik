<p align="center"><img src="img/FlatPik.png" style="width: 300px; margin-bottom:20px"></p>

# FlatPik: the Flatpak App Store for Raspberry Pi
This is FlatPik. It's just a front-end to search and install flatpak apps from Flathub on Raspberry Pi OS, made for fun. That, and for those who doesn't like to use terminal. Everything FlatPik does can be done from console running some commands.

It's almost a single .py file, but it needs some modules. Install them using pip:

```shell
pip install PyQt6 PyQtWebEngine requests
```

or apt:

```shell
sudo apt install python3-pyqt6.qtwebengine python3-requests python3-pyqt6
```

## Features
* Install `flatpak` package and add Flathub PPA, adding full support.
* Install flatpak apps quickly from the "Install" button. Time will depend on package size and needed runtimes. A message will appear on status bar while installing and a pop-up when finished.
* Simultaneous installation support (but not recommended).
* Update all flatpaks at once.
* aarch64 apps only (no x86_64 apps since they're not supported on Raspberry Pi).
* Link to detailed info on app name (official website if website-verified, else Flathub).
* Uninstall button.
* Dark/Light theme.

![Captura de FlatPik](img/popular-apps.png)

## How it works
* After launching for first time, flatpak support shoud not be available. Clicking gear button will install flatpak package and Flathub repository.
* If flatpak support exists, gear will be another one for updating all flatpaks.
* Clicking on a download button will install an app and necessary runtimes.
* If an app exists, an uninstall button will appear. This button will uninstall the app and unnecessary runtimes.
