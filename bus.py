import random


class BusMessage:
    def __init__(self, route:str, code:str, current_stop: str, next_stop:str, distance_left:int, passenger_count:int, capacity:int):
        self.route = route
        self.code = code
        self.current_stop = current_stop
        self.next_stop = next_stop
        self.distance_left = str(distance_left) + "m"
        self.passenger_count = passenger_count
        self.capacity = capacity

    def to_dict(self):
        return self.__dict__

class Route:
    def __init__(self, route:str, stops:list[str], distances:list[int]):
        self.route = route
        self.stops = stops
        self.distances = distances
        self.stops_count = len(self.stops)

        if self.stops_count != len(distances):
            raise ValueError("Stops count doesn't match distances")

    def get_route_name(self) -> str:
        return self.route

    def get_stop_name(self, index) -> str:
        return self.stops[index]

    def get_distance_to_next_stop(self, index) -> int:
        return self.distances[index]


    def get_next_stop_index(self, index) -> int:
        return (index + 1) % self.stops_count

    def is_index_valid(self, index) -> bool:
        return 0 <= index < self.stops_count


class Bus:
    def __init__(self, route: Route, code:str, capacity:int, start_index:int, start_passengers_count:int):
        if not route.is_index_valid(start_index):
            raise ValueError("Invalid start index")

        if start_passengers_count < 0 or start_passengers_count > capacity:
            raise ValueError("Number of passengers at start should be between 0 and capacity")

        self.route = route
        self.code = code
        self.capacity = capacity
        self.passengers_count = start_passengers_count
        self.current_stop = start_index
        self.next_stop = route.get_next_stop_index(start_index)
        self.distance_left = route.get_distance_to_next_stop(self.current_stop)

    def to_message(self) -> BusMessage:
        route = self.route.get_route_name()
        current_stop = self.route.get_stop_name(self.current_stop)
        next_stop = self.route.get_stop_name(self.next_stop)
        return BusMessage(route, self.code, current_stop, next_stop, self.distance_left, self.passengers_count, self.capacity)

    def move(self):
        step = random.randint(5, 150)
        self.distance_left -= step

        while self.distance_left <= 0:
            self.current_stop = self.next_stop
            self.next_stop = self.route.get_next_stop_index(self.current_stop)
            self.update_passenger_count()
            self.distance_left += self.route.get_distance_to_next_stop(self.current_stop)

    def update_passenger_count(self):
        delta = random.randint(-5, 10)
        self.passengers_count = max(0, min(self.capacity, self.passengers_count + delta))

ROUTE_24B = Route(
    route="24B",
    stops=[
        "Disp. Unirii",
        "Colegiul Pedagogic",
        "Iulius Mall Est",
        "Campus Universitar Est",
        "Arte Plastice",
        "Crinului",
        "Somes",
        "Constanta",
        "Sora",
        "Memorandumului N",
        "Spitalul de Copii",
        "Fabrica de Bere",
        "Gradini Manastur",
        "Taberei",
        "Calea Floresti",
        "Nodul N Nord",
        "VIVO",
        "Polus Center",
        "Ciobanului",
        "Piata Flora",
        "Calea Manastur",
        "Agronomia",
        "Calea Motilor",
        "Memorandumului S",
        "Victoria",
        "Regionala CFR",
        "Biserica Sf. Petru",
        "Piata Marasti",
        "Maresal C. Prezan",
        "Dorobantilor",
        "Campus Universitar V",
        "Iulius Mall V",
        "Valeriu Bologa"
    ],
    distances=[
        300, 400, 300, 150, 600, 500, 400, 400,
        300, 600, 550, 600, 500, 600, 700, 800,
        600, 200, 200, 400, 300, 600, 550, 600,
        500, 450, 700, 600, 550, 600, 500, 450,
        600
    ]
)

ROUTE_25 = Route(
    route="25",
    stops=[
        "Disp. Clabucet",
        "Primaverii",
        "Minerva",
        "Izlazului",
        "Calea Manastur",
        "Agronomia",
        "Calea Motilor",
        "Memorandumului S",
        "Victoria",
        "Regionala CFR",
        "Biserica Sf. Petru",
        "Piata Marasti",
        "Maresal C. Prezan",
        "Dorobantilor",
        "Campus Universitar V",
        "Iulius Mall V",
        "Valeriu Bologa",
        "Snagov N",
        "Borsec N",
        "Bistritei",
        "Septimiu Albini N",
        "Piata Cipariu N",
        "Piata Avram Iancu",
        "Sora",
        "Memorandumului N",
        "Spitalul de Copii",
        "Fabrica de Bere",
        "Gradini Manastur",
        "Ion Mester",
        "Peana",
        "Garbau"
    ],
    distances=[
        600, 500, 450, 700,
        600, 550, 600, 500, 450, 700,
        600, 550, 600, 500, 450, 700,
        600, 550, 600, 500, 450, 700,
        600, 550, 600, 500, 450, 700,
        600, 550, 650
    ]
)

ROUTE_DUMMY = Route(
    route="dummy",
    stops=[
        "Stop1",
        "Stop2",
        "Stop3"
    ],
    distances=[100, 200, 200]
)

BUSES: list[Bus] = [
    Bus(ROUTE_DUMMY, "dummy-bus", capacity=30, start_index=0, start_passengers_count=10),
    Bus(ROUTE_24B, "24B-001", capacity=80, start_index=0, start_passengers_count=20),
    Bus(ROUTE_24B, "24B-002", capacity=80, start_index=3, start_passengers_count=45),
    Bus(ROUTE_25,  "25-001",  capacity=60, start_index=1, start_passengers_count=30),
    Bus(ROUTE_25,  "25-002",  capacity=60, start_index=4, start_passengers_count=50),
]
