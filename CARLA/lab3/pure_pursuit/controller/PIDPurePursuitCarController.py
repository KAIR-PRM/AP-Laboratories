from datetime import datetime
import carla
import numpy as np

from ..utils.math import carlaVector3DToNumpy
from ..utils.PID import PID
from .AbstractCarController import AbstractCarController


class PIDPurePursuitCarController(AbstractCarController):
    def __init__(self, world: carla.World, vehicle: carla.Vehicle):
        super().__init__(world, vehicle)

        self.previousTime = datetime.now()

        # TODO: dobierz inne wartości PID (np. spróbuj większe Kp lub dodaj Ki); jakie są najlepsze i dlaczego?
        self.pid = PID(Kp=1.0, Ki=0.02, Kd=0.2)

    def get_lookahead(self):
        # TODO: poeksperymentuj z parametrem lookahead - jaki ma wpływ na zachowanie pojazdu?
        return 5.0

    def drive(self):
        now = datetime.now()

        dt = (now - self.previousTime).total_seconds()

        # TODO: odnajdź w API metodę do pobrania transformacji pojazdu https://carla.readthedocs.io/en/latest/python_api/
        # wskazówka 1: transformacja = lokalizacja (carla.Location) + rotacja (carla.Rotation - kąty pitch, roll, yaw)
        # wskazówka 2: klasa carla.Vehicle dziedziczy po carla.Actor
        transform = ...
        location = ...
        heading_vector = ...  # TODO: znajdź metodę wyliczającą wektor trajektorii obiektu na podstawie jego rotacji

        target_vector = self.waypoint.transform.location - location

        # wyrysuj wektor pojazd-cel
        self.world.debug.draw_arrow(
            location + carla.Location(z=2),
            location + carla.Location(z=2) + target_vector,
            thickness=0.1,
            arrow_size=0.3,
            color=carla.Color(r=255, g=0, b=0),
            life_time=0.1,  # w sekundach
        )

        # konwersja z carla.Vector3D (https://carla.readthedocs.io/en/latest/python_api/#carla.Vector3D) do numpy
        heading_vector = carlaVector3DToNumpy(heading_vector)
        target_vector = carlaVector3DToNumpy(target_vector)

        # wyrysuj wektor trajektorii
        self.debug_draw_trajectory_vector()

        # normalizacja wektorów
        heading_vector /= np.linalg.norm(heading_vector)
        target_vector /= np.linalg.norm(target_vector)

        # TODO: oblicz kąt (ze znakiem) między wektorem trajektorii a wektorem punktu docelowego:
        # w perspektywie, w której układ współrzędnych jest zorientowany zgodnie z wektorem trajektorii
        # (tj. możemy sobie wyobrazić, że 'jest on osią Y tego układu'), chcemy obliczyć kąt między wektorem trajektorii
        # a wektorem celu, tak, aby skręt w lewo był kątem ujemnym, skręt w prawo - dodatnim, a brak konieczności skrętu - 0
        targetAngle = ...
        headingAngle = ...

        # uwaga: należy uwzględnić także możliwość, iż kąt będzie minimalnie różny co do wartości, jednak będzie oznaczał praktycznie tą samą rotację na okręgu,
        # np. -2pi i 2pi co do różnicy są całkiem spore, natomiast logicznie powodują obrót do tego samego "miejsca" na okręgu
        # aby tego uniknąć, należy znormalizować kąt; można też użyć np.unwrap (należy przeczytać dokumentację: https://numpy.org/doc/stable/reference/generated/numpy.unwrap.html)
        targetAngle, headingAngle = ...

        angle = np.rad2deg(targetAngle - headingAngle)

        # TODO: przytnij kąt do zakresu [-maxKątSkrętu, maxKątSkrętu]
        angle = ...

        # TODO: przelicz kąt z zakresu [maxKątSkrętu, maxKątSkrętu] do zakresu [-1, 1] (znormalizowany)
        errorNormalized = ...
        print(
            "Cel",
            self.waypoint.id,
            "Kąt docelowy",
            angle,
            "Błąd",
            errorNormalized,
        )

        # zaktualizuj wartość regulatora PID
        # TODO: wywołaj aktualizację regulatora PID
        steer = ...

        # TODO: przytnij sterowanie do zakresu [-1, 1] - failsafe
        steerNormalized = ...

        control = carla.VehicleControl()
        targetThrottle = self.get_target_throttle(
            steerNormalized=steerNormalized, dt=dt
        )
        control.throttle = targetThrottle
        # TODO: ustaw reverse na True, jeżeli docelowy throttle < 0
        control.reverse = bool(...)
        control.steer = steerNormalized

        self.vehicle.apply_control(control)
        self.debug_draw_waypoint(
            self.waypoint,
            color=carla.Color(r=0, g=255, b=0),
            offset=carla.Location(z=1.0),
        )

        self.previousTime = now
