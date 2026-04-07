import carla

def set_spectator_behind_vehicle(world, vehicle):
    """Positions the spectator camera behind the specified vehicle."""
    spectator = world.get_spectator()
    transform = vehicle.get_transform()
    # Get the forward vector to calculate the offset relative to the vehicle's orientation
    forward_vector = transform.get_forward_vector()

    # Calculate offset: -15 meters back, 6 meters up
    offset = carla.Location(x=-15 * forward_vector.x, y=-15 * forward_vector.y, z=6)
    # Calculate the new spectator transform
    spectator_transform = carla.Transform(
        transform.location + offset,
        # Set rotation: slightly looking down (-20 pitch), same yaw as vehicle
        carla.Rotation(pitch=-20, yaw=transform.rotation.yaw, roll=transform.rotation.roll)
    )
    # Wrap the set_transform call in a try-except block for robustness
    try:
        spectator.set_transform(spectator_transform)
        print("Spectator camera positioned behind the vehicle.")
    except Exception as e:
        print(f"Error setting spectator transform: {e}")