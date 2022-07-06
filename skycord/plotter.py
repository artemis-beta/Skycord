import typing
import SimConnect
import asyncio
import numpy
import pygmt
import datetime
import prompt_toolkit
import keyboard
import skycord.airports as sky_air
import skycord.options as sky_opts


class FlightPlot:
    def __init__(self, timeout: int = 2000) -> None:
        self._way_points: typing.List[numpy.ndarray] = []
        self._record: bool = False
        self._run: bool = True
        self._sim_connect = SimConnect.SimConnect()
        self._request_node = SimConnect.AircraftRequests(self._sim_connect, timeout)
        self._prompt: prompt_toolkit.PromptSession = prompt_toolkit.PromptSession()
        self._airports = sky_air.AirportsDB()
        keyboard.add_hotkey("ctrl+alt+shift+p", self.atc_screenshot)
        keyboard.add_hotkey("ctrl+alt+shift+f", self.dump)

    def atc_screenshot(self) -> None:
        _figure = pygmt.Figure()
        _centre_point: typing.Tuple[float] = (
            self._request_node.get("PLANE_LONGITUDE"),
            self._request_node.get("PLANE_LATITUDE")
        )
        _airports = self._airports.get_nearest_airports(_centre_point[1], _centre_point[0])
        _airports_pos = tuple((i.longitude, i.latitude) for i in _airports)
        _airport_names = tuple(i.icao for i in _airports)
        _region = [
            _centre_point[0] - 1,
            _centre_point[0] + 1,
            _centre_point[1] - 1,
            _centre_point[1] + 1
        ]
        _grid = pygmt.datasets.load_earth_relief(resolution="30s", region=_region, registration='gridline')
        _figure.grdimage(
            grid=_grid,
            cmap=sky_opts.as_string(sky_opts.CMAP.OCEAN),
            projection="M8i",
            frame=True,
            transparency=50,
            verbose='e',
        )
        _figure.grdcontour(
            grid=_grid,
            verbose='e'
        )
        _figure.coast(water="black", rivers="black")
        _figure.plot(data=(_centre_point,), style="c0.3c", color="white", pen="black")

        for airport, name in zip(_airports_pos, _airport_names):
            _figure.plot(data=(airport,), style="c0.3c", color="#feeebb", pen="black")
            _figure.text(text=name, x=airport[0], y=airport[1], offset='0.5', font="22p,Helvetica-Bold,#e7e6e6")
        _timestamp: str = datetime.datetime.strftime(datetime.datetime.now(), "atc_%d_%m_%Y_%H_%M_%S.png")
        _figure.colorbar(frame=["a500", "x+lElevation", "y+lm"])
        _figure.savefig(_timestamp)

    def check_similar(self, new_coord: typing.Tuple[int, int, int], tolerance: int = 10) -> bool:
        try:
            _prev_coord: typing.Tuple[int, int, int] = self._way_points[-1]
            return all(abs(i-j) < tolerance for i, j in zip(new_coord, _prev_coord))
        except IndexError:
            return False

    async def monitor(self, every_sec: int = 10) -> None:
        """Monitor MSFS for plane coordinates"""
        if not self._request_node.get("ELECTRICAL_MASTER_BATTERY"):
            self._run = False
            print("Aircraft not available/powered on, aborting.")
            return

        while self._run:
            if not self._record:
                await asyncio.sleep(1)
                continue

            _coord_candidate: numpy.ndarray = numpy.float64([
                self._request_node.get("PLANE_LONGITUDE"),
                self._request_node.get("PLANE_LATITUDE"),
                self._request_node.get("PLANE_ALTITUDE")
            ])

            if not self.check_similar(_coord_candidate):
                print(_coord_candidate)
                self._way_points.append(_coord_candidate)

            await asyncio.sleep(every_sec)

    def dump(self) -> None:
        """Dump flight path"""
        _figure = pygmt.Figure()
        _minlat: float = min(numpy.array(self._way_points)[:, 1])
        _maxlat: float = max(numpy.array(self._way_points)[:, 1])
        _minlon: float = min(numpy.array(self._way_points)[:, 0])
        _maxlon: float = max(numpy.array(self._way_points)[:, 0])

        _rangelat: float = abs(_maxlat-_minlat)
        _rangelon: float = abs(_maxlon-_minlon)

        _region = [
            _minlon-0.5*_rangelon,
            _maxlon+0.5*_rangelon,
            _minlat-0.5*_rangelat,
            _maxlat+0.5*_rangelat
        ]
        _airports = self._airports.get_nearest_airports(_minlat+0.5*_rangelat, _minlon+0.5*_rangelon)
        _airports_pos = tuple((i.longitude, i.latitude) for i in _airports)
        _airport_names = tuple(i.icao for i in _airports)
        _grid = pygmt.datasets.load_earth_relief(resolution="30s", region=_region, registration='gridline')
        _figure.grdimage(
            grid=_grid,
            cmap=sky_opts.as_string(sky_opts.CMAP.OCEAN),
            projection="M8i",
            frame=True,
            transparency=50,
            verbose='e',
        )
        _figure.grdcontour(
            grid=_grid,
            verbose='e'
        )
        _figure.plot(data=self._way_points, pen="1p,red")
        for airport, name in zip(_airports_pos, _airport_names):
            _figure.plot(data=(airport,), style="c0.3c", color="#feeebb", pen="black")
            _figure.text(text=name, x=airport[0], y=airport[1], offset='0.5', font="22p,Helvetica-Bold,#e7e6e6")
        _timestamp: str = datetime.datetime.strftime(datetime.datetime.now(), "flight_%d_%m_%Y_%H_%M_%S.png")
        _figure.colorbar(frame=["a500", "x+lElevation", "y+lm"])
        _figure.savefig(_timestamp)

    def reset(self) -> None:
        """Reset plotting of coordinates"""
        self._way_points = []

    async def prompt(self) -> None:
        await asyncio.sleep(1)
        while self._run:
            try:
                _command: str = await self._prompt.prompt_async(":> ")
                if _command.upper() == "RESET":
                    self.reset()
                elif _command.upper() == "RUN":
                    print("YAY")
                    self._record = True
                elif _command.upper() == "STOP":
                    self._record = False
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                return

    async def launch(self) -> None:
        try:
            await asyncio.wait([
                asyncio.create_task(self.prompt()),
                asyncio.create_task(self.monitor())
            ])
        except KeyboardInterrupt:
            self._run = False

if __name__ in "__main__":
    _plot = FlightPlot()
    asyncio.run(_plot.launch())