# Skycord

**NOTE:** Still under development!

Map plotter for Microsoft Flight Simulator. This project is under development as a way of recording flight paths and displaying the current global position of the user.

## Installation

Currently the module is only usable via the [Poetry](https://python-poetry.org/) development environment, this is installable using `pip`:

```sh
pip install poetry
```

You will also need to install the [Generic Mapping Tools](https://github.com/GenericMappingTools/gmt/releases/tag/6.4.0) library.

When poetry is available, clone this repository:

```sh
git clone --recurse-submodules https://github.com/artemis-beta/Skycord.git
```

build and launch the virtual environment by running within the repository:

```sh
poetry install
```

```sh
poetry shell
```

## Usage

Within the virtual environment run the plotter script:

```sh
python skycord/plotter.py
```

this will launch a CLI. Make sure you have MSFS open and have started a flight.

### Location Snapshot

With a flight in session the shortcut `CTRL+SHIFT+ALT+P` will create a location map of the current position.

### Flight Record

To record a flight path type "run" in the CLI and continue flying. You can dump the output path using the keyboard shortcut `CTRL+SHIFT+ALT+F` at any time.