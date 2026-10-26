import math
import sys

import matplotlib.pyplot as plt
import numpy as np

G = 9.80665  # m/s^2
AIR_DENSITY = 1.225  # kg/m^3 at sea level


def ask_float(prompt, valid, error):
    value = float(input(prompt))
    if not valid(value):
        sys.exit(f"Error: {error}")
    return value


def ask_yes_no(prompt):
    answer = input(prompt).strip().lower()
    if answer not in ("y", "n"):
        sys.exit("Error: please answer y or n.")
    return answer == "y"


def without_drag(v0, angle, y0):
    vx = v0 * math.cos(angle)
    vy = v0 * math.sin(angle)

    # positive root of y0 + vy*t - g*t^2/2 = 0
    t_flight = (vy + math.sqrt(vy**2 + 2 * G * y0)) / G
    t = np.linspace(0, t_flight, 500)
    x = vx * t
    y = y0 + vy * t - 0.5 * G * t**2
    return t, x, y


def with_drag(v0, angle, y0, rho, cd, area, mass, dt=0.001):
    k = 0.5 * cd * rho * area / mass
    t, x, y = [0.0], [0.0], [y0]
    vx, vy = v0 * math.cos(angle), v0 * math.sin(angle)

    # forward Euler until the projectile drops below the ground
    while y[-1] >= 0:
        v = math.hypot(vx, vy)
        ax = -k * v * vx
        ay = -G - k * v * vy
        x.append(x[-1] + vx * dt)
        y.append(y[-1] + vy * dt)
        t.append(t[-1] + dt)
        vx += ax * dt
        vy += ay * dt

    return np.array(t), np.array(x), np.array(y)


def plot(x, y, title):
    plt.plot(x, y)
    plt.xlim(0, x.max())
    plt.ylim(0, y.max() * 1.1)
    plt.xlabel("Horizontal position (m)")
    plt.ylabel("Height (m)")
    plt.title(title)
    plt.grid(True)
    plt.show()


def main():
    no_drag = ask_yes_no("Simulate without air resistance? (y/n): ")

    v0 = ask_float("Initial velocity (m/s): ", lambda v: v >= 0, "initial velocity must be positive.")
    angle_deg = ask_float("Launch angle (deg): ", lambda a: 0 <= a <= 90, "launch angle must be between 0 and 90 degrees.")
    y0 = ask_float("Launch height (m): ", lambda h: h >= 0, "launch height must be zero or positive.")
    angle = math.radians(angle_deg)

    if no_drag:
        t, x, y = without_drag(v0, angle, y0)
        title = "Projectile trajectory"
    else:
        if ask_yes_no("Use sea-level air density? (y/n): "):
            rho = AIR_DENSITY
        else:
            rho = ask_float("Air density (kg/m^3): ", lambda r: r > 0, "air density must be positive.")
        cd = ask_float("Drag coefficient: ", lambda c: c > 0, "drag coefficient must be positive.")
        area = ask_float("Cross-sectional area (m^2): ", lambda a: a > 0, "cross-sectional area must be positive.")
        mass = ask_float("Mass (kg): ", lambda m: m > 0, "mass must be positive.")
        t, x, y = with_drag(v0, angle, y0, rho, cd, area, mass)
        title = "Projectile trajectory with air resistance"

    print(f"Time of flight: {t[-1]:.2f} s")
    print(f"Horizontal range: {x[-1]:.2f} m")
    plot(x, y, title)


if __name__ == "__main__":
    main()
