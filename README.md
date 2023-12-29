# FlatPik: the Flatpak App Store for Raspberry Pi

This is FlatPik. It's just a front-end to search and install flatpak apps from Flathub on Raspberry Pi OS, made for fun. That, and for those who doesn't like to use terminal.

It's just a .py file (this could change), but it needs modules like Qt5 and requests. Install them using pip or apt. You can create a virtual environment (venv) too.

## Features

* Install `flatpak` package and add Flathub PPA.
* aarch64 apps only (no x86_64 apps since they're not supported on Raspberry Pi).
* Install flatpak apps quickly from the "Install" button. Time will depend on package size and needed runtimes.

![Captura de FlatpPik](capturas/featured.png)

## Roadmap

This is a work in progress; not finished at all. Coming soon.

* Messages and info abount install progress.
* App icon for FlatPik.
* Maybe: Uninstall button.
* Maybe: Light theme.
