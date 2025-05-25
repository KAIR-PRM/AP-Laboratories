from pynput import keyboard
import carla
import random
import numpy as np
import cv2

from .controller.AbstractCarController import AbstractCarController

# TODO: zaimportuj klasę CarController
...

# TODO: zaimportuj klasę LateralLookaheadPurePursuitCarController
...

from .ControllerStrategy import ControllerStrategy

# Konfiguracja strategii pojazdu
# TODO: dostosuj tą wartość w zależności od potrzeb
controllerStrategy = ControllerStrategy.PID_PURE_PURSUIT

# ustaw na True, aby spektator podążał za autem
SPECTATOR_FOLLOW_CAR = True

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

print("Wciśnij q, by wyjść")

for vehicle in world.get_actors().filter("vehicle.*"):
    vehicle.destroy()

vehicle_blueprints = world.get_blueprint_library().filter("vehicle.ford.crown")
rand_vehicle_blueprint = random.choice(vehicle_blueprints)
spawn_points = world.get_map().get_spawn_points()

spawn_point = spawn_points[1]
vehicle = world.spawn_actor(rand_vehicle_blueprint, spawn_point)

transform = vehicle.get_transform()

location = spawn_point.location + carla.Location(x=-5, z=3)
rotation = spawn_point.rotation
spectator = world.get_spectator()
spectator.set_transform(carla.Transform(location, rotation))

try:
    run = True

    def onPress(key):
        global run

        try:
            if key.char == "q":
                run = False
        except AttributeError:
            # pomiń klawisze specjalne
            pass

    camera_bp = world.get_blueprint_library().find("sensor.camera.rgb")
    camera_bp.set_attribute("image_size_x", "800")
    camera_bp.set_attribute("image_size_y", "600")
    camera_bp.set_attribute("fov", "90")

    camera_transform = carla.Transform(carla.Location(x=0.3, z=1.1, y=-0.4))

    # dodaj kamerę do pojazdu
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    img_array = None

    def process_image(image):
        global img_array
        # konwersja z surowego formatu na numpy array uint8
        img_array = np.frombuffer(image.raw_data, dtype=np.uint8)
        img_array = img_array.reshape((image.height, image.width, 4))  # format: BGRA
        # TODO: dane w img_array są w formacie BGRA; usuń kanał alfa
        img_array = ...

    # dodaj callback nasłuchujący na przychodzący obraz
    camera.listen(lambda image: process_image(image))

    listener = keyboard.Listener(on_press=onPress)
    listener.start()

    carController: AbstractCarController

    if controllerStrategy == ControllerStrategy.PID_PURE_PURSUIT:
        carController = PIDPurePursuitCarController(world=world, vehicle=vehicle)
    elif controllerStrategy == ControllerStrategy.LATERAL_LOOKAHEAD_PURE_PURSUIT:
        carController = LateralLookaheadPurePursuitCarController(
            world=world, vehicle=vehicle
        )
    else:
        raise RuntimeError(
            f"Unknown car controller strategy '{controllerStrategy}' chosen"
        )

    cv2.namedWindow("RGB onboard cam", cv2.WINDOW_NORMAL)

    while run:
        carController.maybe_advance_waypoint()
        carController.drive()

        if SPECTATOR_FOLLOW_CAR:
            transform = vehicle.get_transform()
            location = transform.location + carla.Location(z=10)
            rotation = transform.rotation

            # TODO: ustaw spektatora z tyłu auta i nad nim
            moveBackwardsBy = 10
            yawRad = np.deg2rad(rotation.yaw)
            offsetX = -moveBackwardsBy * np.cos(yawRad)
            offsetY = -moveBackwardsBy * np.sin(yawRad)

            ...  # x
            ...  # y

            ...  # pitch

            spectator.set_transform(carla.Transform(location, rotation))

        if img_array is not None:
            cv2.imshow("RGB onboard cam", img_array)

        cv2.waitKey(1)
        world.tick()

    cv2.destroyAllWindows()
finally:
    # na koniec skryptu zawsze usuń auto z mapy, również w przypadku błędu
    vehicle.destroy()
    camera.destroy()
