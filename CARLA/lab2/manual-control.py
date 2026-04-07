from pynput import keyboard
import carla
import numpy as np
import cv2
from typing import Set

THROTTLE_STEP = 0.03
STEER_STEP = 0.06

print("Łączenie z CARLĄ...")
client = carla.Client("localhost", 2000)
client.set_timeout(10.0)

print("Sprawdzanie mapy...")

world = client.get_world()
print(world.get_map().name)
# dla CARLA 0.9
if "Town04_Opt" in client.get_available_maps():
    if "Town04_Opt" not in world.get_map().name:
        print("Ładowanie mapy Town04_Opt")
        client.load_world("Town04_Opt")
        world = client.get_world()
# dla CARLA 0.10
elif "Town10HD_Opt" not in world.get_map().name:
    print("Ładowanie mapy Town10HD_Opt")
    client.load_world("Town10HD_Opt")
    world = client.get_world()
else:
    print("Właściwa mapa jest już załadowana")

print("Wciśnij a, by skręcić w lewo")
print("Wciśnij d, by skręcić w prawo")
print("Wciśnij w, by przyspieszyć")
print("Wciśnij s, by zmniejszyć prędkość")
print("Wciśnij q, by wyjść")

for vehicle in world.get_actors().filter("vehicle.*"):
    vehicle.destroy()

vehicle_blueprint = world.get_blueprint_library().filter("vehicle.ford.crown")[0]
spawn_points = world.get_map().get_spawn_points()

vehicle = world.spawn_actor(vehicle_blueprint, spawn_points[2])

pressedKeys: Set[str] = set()

try:
    throttle = 0.0
    steer = 0.0

    def onPress(key):
        try:
            # TODO: obsłuż odczytanie znaku z eventu, dodając go do pressedKeys - https://pynput.readthedocs.io/en/latest/keyboard.html
            ...
        except AttributeError:
            # pomiń klawisze specjalne
            pass

    def onRelease(key):
        try:
            # TODO: obsłuż odczytanie znaku z eventu, usuwając go z pressedKeys - https://pynput.readthedocs.io/en/latest/keyboard.html
            ...
        except AttributeError:
            # pomiń klawisze specjalne
            pass

    # TODO: dodaj kamerę RGB o rozdzielczości 800x600 oraz FOV 90 stopni
    # https://carla.readthedocs.io/en/latest/ref_sensors/#rgb-camera
    # https://carla.readthedocs.io/en/latest/python_api/#carla.ActorBlueprint.set_attribute
    camera_bp = ...
    ...
    ...
    ...

    # TODO: ustaw transformację na siedzenie przedniego kierowcy (tzn. widok kierowcy siedzącego w pojeździe)
    camera_transform = ...

    # dodaj kamerę do pojazdu
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    img = None

    def process_image(image):
        global img
        # konwersja z surowego formatu na numpy array uint8
        img = np.frombuffer(image.raw_data, dtype=np.uint8)

        # dane w img_array są obecnie wektorem 1x(width * height * 4) - spłaszczoną do postaci wektora 1-wymiarowego bitmapą height x width w formacie BGRA (4 kanały głębi)
        # TODO: przekształć ten wektor na macierz height x width x 4 (uwaga: kolejność wymiarów ma znaczenie)
        img = ...

        # TODO: piksele w img_array są w wektorami 4-elementowymi o kolejności BGRA; usuń kanał alfa, używając slicingu: https://numpy.org/doc/stable/user/basics.indexing.html#dimensional-indexing-tools
        img = ...

        # TODO: wyświetl przyspieszenie i skręt kół na obrazie
        ...

    # dodaj callback nasłuchujący na przychodzący obraz
    camera.listen(lambda image: process_image(image))

    listener = keyboard.Listener(on_press=onPress, on_release=onRelease)
    listener.start()

    cv2.namedWindow("RGB onboard cam", cv2.WINDOW_NORMAL)

    spectator = world.get_spectator()

    while True:
        # TODO: obsłuż wciśnięte przyciski, dodając / odejmując STEER_STEP / THROTTLE_STEP, lub przerywając pętlę
        if "a" in pressedKeys:
            ...
        elif "d" in pressedKeys:
            ...
        elif "w" in pressedKeys:
            ...
        elif "s" in pressedKeys:
            ...
        elif "q" in pressedKeys:
            print("Kończenie programu")
            ...

        steer = np.clip(steer, -0.65, 0.65)
        throttle = np.clip(throttle, -1, 1)

        print(f"Przyspieszenie: {throttle}, skręt kół: {steer}")
        vehicle.apply_control(
            carla.VehicleControl(
                throttle=abs(float(throttle)),
                steer=float(steer),
                reverse=bool(throttle < 0),
            )
        )

        transform = vehicle.get_transform()

        # TODO: ustaw spectatora na pozycję nad autem, aby było w polu widzenia
        location = ...
        rotation = transform.rotation

        spectator.set_transform(carla.Transform(location, rotation))

        if "w" not in pressedKeys and "s" not in pressedKeys:
            # martwa strefa -0.01 ~ 0.01 -> 0.0
            if abs(throttle) > 0.01:
                throttle *= 0.65  # zanik wykładniczy
            else:
                throttle = 0.0

        if "a" not in pressedKeys and "d" not in pressedKeys:
            # martwa strefa -0.01 ~ 0.01 -> 0.0
            if abs(steer) > 0.01:
                steer *= 0.85  # zanik wykładniczy
            else:
                steer = 0.0

        if img is not None:
            cv2.imshow("RGB onboard cam", img)

        cv2.waitKey(1)
        world.tick()

    cv2.destroyAllWindows()
finally:
    # na koniec skryptu zawsze usuń auto z mapy, również w przypadku błędu
    vehicle.destroy()
    camera.destroy()
