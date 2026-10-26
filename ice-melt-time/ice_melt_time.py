import math
import sys

from scipy import integrate

# Ice
RHO = 917  # kg/m^3
C_ICE = 2100  # J/(kg K)
LATENT_HEAT = 3.34e5  # J/kg

# Radiation
EMISSIVITY = 0.95
SIGMA = 5.670374419e-8  # W/(m^2 K^4)

MELTING_POINT = 273.15  # K


def ask_float(prompt, valid, error):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a number.")
            continue
        if valid(value):
            return value
        print(error)


def melt_time(radius, t_freezer, t_room):
    """Seconds for an ice sphere to warm from t_freezer to 0 C and then melt (temps in K)."""
    area = 4 * math.pi * radius**2
    mass = RHO * 4 / 3 * math.pi * radius**3

    # natural convection coefficient, scaled with the temperature difference
    h = 10 * (abs(310.15 - t_room) / 17) ** 0.25

    def heat_flux(t):
        return h * (t_room - t) + EMISSIVITY * SIGMA * (t_room**4 - t**4)

    # stage 1: warm the whole block up to the melting point
    t_warm, _ = integrate.quad(lambda t: mass * C_ICE / (area * heat_flux(t)), t_freezer, MELTING_POINT)

    # stage 2: the surface recedes at a constant rate while held at 0 C
    t_melt = radius * RHO * LATENT_HEAT / heat_flux(MELTING_POINT)

    return t_warm + t_melt


def main():
    radius = ask_float("Initial radius of the ice sphere (m): ", lambda r: r > 0, "Radius must be greater than zero.")
    t_freezer = ask_float("Freezer temperature (C): ", lambda t: -273.15 <= t <= 0, "Freezer temperature must be between -273.15 and 0 C.")
    t_room = ask_float("Room temperature (C): ", lambda t: t >= -273.15, "Temperature cannot be below absolute zero.")

    if t_room <= 0:
        sys.exit("The room is at or below 0 C, so the ice will not melt.")

    total = melt_time(radius, t_freezer + 273.15, t_room + 273.15)
    hours, rest = divmod(total, 3600)
    minutes, seconds = divmod(rest, 60)
    print(f"Time to melt: {int(hours)} h {int(minutes)} min {seconds:.2f} s")


if __name__ == "__main__":
    main()
