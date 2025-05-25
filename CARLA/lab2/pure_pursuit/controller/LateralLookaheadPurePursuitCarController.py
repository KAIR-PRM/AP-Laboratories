from datetime import datetime
import carla
import numpy as np

from .AbstractCarController import AbstractCarController
from ..utils.math import carlaVector3DToNumpy


class LateralLookaheadPurePursuitCarController(AbstractCarController):
    def __init__(self, world: carla.World, vehicle: carla.Vehicle):
        super().__init__(world, vehicle)

        self.previousTime = datetime.now()

        self.K_dd = 4
        self.max_L_d = 6
        self.min_L_d = 0.5

        self.L = self.get_wheelbase()

    def get_wheelbase(self):
        """Oblicza rozstaw osi (przednia-tylna) kół"""

        # https://en.wikipedia.org/wiki/Ford_Crown_Victoria
        return 2.906

    def get_lookahead(self):
        # TODO: poeksperymentuj z parametrem lookahead - jaki ma wpływ na zachowanie pojazdu?
        return np.clip(self.K_dd * self.speed, self.min_L_d, self.max_L_d)

    def drive(self):
        now = datetime.now()

        dt = (now - self.previousTime).total_seconds()

        # TODO: odnajdź w API metodę do pobrania transformacji pojazdu https://carla.readthedocs.io/en/latest/python_api/
        # wskazówka 1: transformacja = lokalizacja (carla.Location) + rotacja (carla.Rotation - kąty pitch, roll, yaw)
        # wskazówka 2: klasa carla.Vehicle dziedziczy po carla.Actor
        transform = ...
        location = transform.location
        heading_vector = carlaVector3DToNumpy(
            ...
        )  # TODO: znajdź metodę wyliczającą wektor trajektorii obiektu na podstawie jego rotacji

        target_vector = carlaVector3DToNumpy(
            self.waypoint.transform.location - location
        )

        # wyrysuj wektor trajektorii
        self.debug_draw_trajectory_vector()

        # normalizacja wektorów
        heading_vector /= np.linalg.norm(heading_vector)
        target_vector /= np.linalg.norm(target_vector)

        # TODO: oblicz kąt (ze znakiem) między wektorem trajektorii a wektorem punktu docelowego:
        # w perspektywie, w której układ współrzędnych jest zorientowany zgodnie z wektorem trajektorii
        # (tj. możemy sobie wyobrazić, że 'jest on osią Y tego układu'), chcemy obliczyć kąt między wektorem trajektorii
        # a wektorem celu, tak, aby skręt w lewo był kątem ujemnym, skręt w prawo - dodatnim, a brak konieczności skrętu - 0
        errorAngle = ... - ...

        # TODO: wzór na kąt skrętu to 2 * self.L * sin(errorAngle) / self.get_lookahead(); upewnij się, że przypisana wartość jest wyrażona w stopniach (jednostka używana w CARLA)
        steeringTargetAngle = ...

        # TODO: przytnij kąt do zakresu [-maxKątSkrętu, maxKątSkrętu]
        steeringTargetAngle = ...

        # TODO: przelicz kąt z zakresu [maxKątSkrętu, maxKątSkrętu] do zakresu [-1, 1] (znormalizowany)
        steerNormalized = ...

        control = carla.VehicleControl()
        targetThrottle = self.get_target_throttle(
            steerNormalized=steerNormalized, dt=dt
        )
        control.throttle = np.abs(targetThrottle)
        control.reverse = bool(targetThrottle < 0)
        control.steer = steerNormalized

        self.vehicle.apply_control(control)
        self.debug_draw_waypoint(self.waypoint)

        self.previousTime = now
