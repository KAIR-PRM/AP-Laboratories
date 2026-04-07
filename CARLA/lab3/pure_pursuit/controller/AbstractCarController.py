import carla
import numpy as np

from ..utils.PID import PID
from typing import Union

DISTANCE = 1.0
TARGET_SPEED_KMPH = 60


class AbstractCarController:
    """Podstawowa klasa abstrakcyjna kontrolera pojazdu, dostarczająca wspólny interfejs API dla implementacji
    (wzorzec projektowy strategia) oraz współdzielone implementacje logiki (DRY - Don't Repeat Yourself)
    """

    def __init__(self, world: carla.World, vehicle: carla.Vehicle):
        """Tworzy instancję kontrolera samochodu nawigującego zadany pojazd po zadanej mapie"""

        self.world = world
        self.vehicle = vehicle
        self.map = world.get_map()

        self.speed = TARGET_SPEED_KMPH / 3.6

        self.waypoint = self.generateWaypoint()

        self.maxWheelSteerAngle = self.get_max_steer_angle()

        self.throttlePid = PID(Kp=0.5, Ki=0.05, Kd=0.1)

    def generateWaypoint(self):
        """Zwraca najbliższy możliwy punkt kluczowy na pasie do jazdy w pobliżu pojazdu"""

        transform = self.vehicle.get_transform()
        location = transform.location

        return self.map.get_waypoint(
            location, project_to_road=True, lane_type=carla.LaneType.Driving
        )

    def is_waypoint_reached(self):
        """Sprawdza, czy obecny punkt docelowy (self.waypoint) został już osiągnięty"""

        location = self.vehicle.get_location()
        distance = location.distance(self.waypoint.transform.location)

        # sprawdź, czy jesteśmy odpowiednio blisko
        if distance < DISTANCE:
            print("Pojazd minął waypoint (odległość)")
            return True

        # ...możliwe jest też, że pojazd odpowiednio szybko wyminął waypoint - sprawdźmy również kierunek wektora
        # dot product będzie > 0, gdy pojazd przejechał zgodnie z kierunkiem waypointa

        vecVehicleToWaypoint = location - self.waypoint.transform.location
        waypointForwardVec = self.waypoint.transform.get_forward_vector()

        dot = (
            vecVehicleToWaypoint.x * waypointForwardVec.x
            + vecVehicleToWaypoint.y * waypointForwardVec.y
        )

        if dot > 0 and distance < 10 * DISTANCE:
            print("Pojazd minął waypoint (dot product)")
            return True

        return False

    def maybe_advance_waypoint(self):
        """Jeżeli obecny waypoint został osiągnięty, pobiera nowy punkt trasy, do którego samochód powinien się kierować"""

        if not self.is_waypoint_reached():
            return None

        next_waypoints = self.waypoint.next(self.get_lookahead())

        if next_waypoints:
            self.waypoint = next_waypoints[
                0
            ]  # wybierz pierwszy wariant dostępnej trasy
            print("Nowy cel z obecnej trasy: ", self.waypoint)
            return self.waypoint

        print("Nowy cel z nowej trasy: ", self.waypoint)
        self.waypoint = self.generateWaypoint()
        return self.waypoint

    def drive(self):
        """Powoduje, że samochód porusza się w kierunku przekazanego punktu trasy"""
        ...

    def get_max_steer_angle(self) -> Union[int, float]:
        """Zwraca maksymalny kąt skrętu pojazdu (w stopniach)"""

        # TODO: pobierz obiekt z informacjami dot. fizyki pojazdu: https://carla.readthedocs.io/en/latest/python_api/#carla.Vehicle.get_physics_control
        wheelPhysicsControl = ...

        # TODO: sprawdź, która składowa klasy WheelPhysicsControl zawiera max kąt skrętu (pomoc: https://github.com/carla-simulator/carla/blob/ue5-dev/LibCarla/source/carla/rpc/WheelPhysicsControl.h)
        return ...

    def get_lookahead(self) -> Union[int, float]:
        """Pobiera odległość kontekstu przeglądanego przed autem, używaną do znalezienia następnego punktu trasy"""
        return DISTANCE

    def debug_draw_trajectory_vector(self):
        """Rysuje wektor trajektorii ("wprzód") pojazdu jako strzałkę"""

        transform = self.vehicle.get_transform()
        location = transform.location

        self.world.debug.draw_arrow(
            location + carla.Location(z=2),
            location + carla.Location(z=2) + transform.get_forward_vector(),
            thickness=0.1,
            arrow_size=0.3,
            color=carla.Color(r=0, g=0, b=255),
            life_time=0.1,  # w sekundach
        )

    def get_target_throttle(self, steerNormalized: float, dt: float):
        """Zwraca docelowe przyspieszenie pojazdu, po uwzględnieniu regulatora"""

        # TODO: przelicz prędkość (velocity, wektorową wielkość) na szybkość (speed, skalarną wartość)
        velocity = self.vehicle.get_velocity()
        current_speed = ...

        # TODO: spraw, by pojazd nie dodawał gazu na zakrętach - niech:
        # speedScalingFactor = 1 gdy steerNormalized = 0
        # speedScalingFactor = ... dla steerNormalized > 0 i < 1
        # speedScalingFactor = 0 (lub nawet -1, co będzie oznaczało ruch w tył) gdy steerNormalized = 1
        speedScalingFactor = ...

        return np.clip(
            self.throttlePid.step(
                (self.speed * speedScalingFactor) - current_speed, dt
            ),
            -1,
            1,
        )

    def debug_draw_waypoint(
        self,
        waypoint: carla.Waypoint,
        time_sec: float = 0.5,
        color=carla.Color(r=0, g=255, b=0),
        offset=carla.Location(),
    ):
        """Rysuje debugowy waypoint 'trwający' (tj. wyświetlany przez) time_sec sekund na mapie"""

        # TODO: zaimplementuj funkcjonalność rysowania strzałki w miejscu waypointu
        # skorzystaj z metody draw_point: https://carla.readthedocs.io/en/latest/python_api#carla.DebugHelper.draw_point
        location = ...
        forward_vector = ...
        end_location = location + forward_vector * 2.0

        location += carla.Location(z=1.5) + offset
        end_location += carla.Location(z=1.5) + offset

        ...
