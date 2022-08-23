from typing import List, Tuple, Dict
import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json


class GPSCoords:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_tuple(self) -> Tuple[float]:
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"GPSCoords({self.x}, {self.y})"


class Neighbourhood:
    def __init__(self, name: str, short_name: str, path: mplPath.Path) -> None:
        self.name = name
        self.short_name = short_name
        self.path = path
        self.frequency = 0

    def __repr__(self) -> str:
        return self.name

    def add_frequency(self, amount: int) -> None:
        self.frequency += amount


class Stop:
    def __init__(self, stop_code: int, coords: GPSCoords) -> None:
        self.stop_code = stop_code
        self.coords = coords
        self.frequency = 0

    def __repr__(self) -> str:
        return f"Stop({self.stop_code}, {self.coords}, {self.frequency})"

    def is_within(self, neighbourhood: Neighbourhood) -> bool:
        return neighbourhood.path.contains_point(self.coords.to_tuple())

def get_stops(data: str) -> Dict[int, Stop]:
    """
    return {stop_id, Stop}
    """
    stops = {}

    with open(data, "r") as f:
        # skip header
        f.readline()
   
        lines = f.readlines()
        for line in lines:
            line = line.split(",")
            try:
                stops[int(line[3])] = Stop(int(line[1]), GPSCoords(float(line[2]), float(line[0])))
            except ValueError:
                continue

    return stops

def get_stop_times(data: str) -> Dict[int, int]:
    """
    return {stop_id, frequency}
    """
    stop_times = {}
    # prevent duplicates
    stop_time_arrivals = set()

    with open(data, "r") as f:
        # skip header
        f.readline()
   
        lines = f.readlines()
        for line in lines:
            line = line.split(",")
            try:
                if int(line[3]) not in stop_times:
                    stop_times[int(line[3])] = 1
                elif int(line[3]) in stop_times and f"{line[3]}-{line[1]}" not in stop_time_arrivals:
                    stop_times[int(line[3])] += 1
                stop_time_arrivals.add(f"{line[3]}-{line[1]}")
            except ValueError:
                continue

    return stop_times

def get_neighbourhoods(data: str) -> List[Neighbourhood]:
    neighbourhoods = []
    with open(data, "r") as f:
        json_neighbourhoods = json.load(f)
        for n in json_neighbourhoods:
            name = n["fields"]["name"]
            short_name = n["fields"]["mapid"]
            coordinates = n["fields"]["geom"]["coordinates"][0]
            path = mplPath.Path(np.array(coordinates))
            neighbourhoods.append(Neighbourhood(name, short_name, path))


    return neighbourhoods

def generate_plot(neighbourhoods: List[Neighbourhood]) -> None:
    fig = plt.figure()
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    x = [neighbourhood.short_name for neighbourhood in neighbourhoods]
    y = [neighbourhood.frequency for neighbourhood in neighbourhoods]
    ax.bar(x, y)

    handles = [
        mpatches.Patch(label=f"{neighbourhood.short_name}: {neighbourhood.name}") for neighbourhood in neighbourhoods
    ]
    plt.legend(handles=handles)
    plt.title("Transit Vehicle Frequencies by Vancouver Neighbourhoods")

    plt.show()


def main():
    stops = get_stops("./data/stops.txt")
    stop_times = get_stop_times("./data/stop_times.txt")

    # get stop frequencies into Stops
    for key, val in stop_times.items():
        stops[key].frequency = val

    neighbourhoods = get_neighbourhoods("./data/vanNeighbours.json")

    for stop in stops.values():
        for neighbourhood in neighbourhoods:
            if stop.is_within(neighbourhood):
                neighbourhood.add_frequency(stop.frequency)

    generate_plot(neighbourhoods)


main()
