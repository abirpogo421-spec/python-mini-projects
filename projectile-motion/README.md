# Projectile Motion

Plots the trajectory of a projectile launched from a given height, speed and angle.

Without air resistance the path is solved exactly. With air resistance, the drag force

$$F_d = \tfrac{1}{2} \rho C_d A v^2$$

acts opposite the velocity, and the equations of motion are integrated with Euler's method (time step 1 ms) until the projectile reaches the ground.

## Usage

```bash
python projectile_motion.py
```

The script asks for the launch conditions and, for the drag case, the air density, drag coefficient, cross-sectional area and mass. It prints the time of flight and horizontal range, then shows the trajectory.

For example, a soccer ball ($C_d = 0.47$, $A = 0.038\ \text{m}^2$, $m = 0.45\ \text{kg}$) kicked at 20 m/s and 45° travels 40.8 m in a vacuum but 24.1 m in air.
