import dataclasses
import json
import typing
import os.path
import numpy


@dataclasses.dataclass
class Airport:
    name: str
    icao: str
    latitude: float
    longitude: float
    elevation: float

class AirportsDB:
    def __init__(self) -> None:
        self._airports: typing.Dict[str, Airport] = self._get_airport_list()

    def _get_airport_list(self) -> typing.Dict:
        _out_dict: typing.Dict[str, Airport] = {}
        with open(os.path.join(os.path.dirname(__file__), "Airports", "airports.json"), encoding = 'cp850') as airfile:
            _airports: typing.Dict = json.load(airfile)

        for airport, data in _airports.items():
            _out_dict[airport] = Airport(
                name=data["name"],
                icao=data["icao"],
                latitude=data["lat"],
                longitude=data["lon"],
                elevation=data["elevation"]
            )
        return _out_dict

    def get_nearest_airports(self, latitude: float, longitude: float, tolerance: float = 1.0) -> typing.List[Airport]:
        _centre = numpy.array([latitude, longitude])
        _candidates: typing.List[Airport] = []

        for airport in self._airports.values():
            _airport_loc = numpy.array([airport.latitude, airport.longitude])
            if numpy.linalg.norm(abs(_airport_loc-_centre)) <= tolerance:
                _candidates.append(airport)

        return _candidates
