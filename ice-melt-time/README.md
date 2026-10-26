# Ice Melt Time

Estimates how long a sphere of ice taken out of a freezer takes to melt completely in a warm room.

The block gains heat from the room by natural convection and thermal radiation. The calculation has two stages:

1. **Warming.** The block heats from the freezer temperature to 0 °C. The time is found by integrating

   $$t_1 = \int_{T_f}^{273.15} \frac{m c}{A\left[h (T_r - T) + \varepsilon \sigma (T_r^4 - T^4)\right]}\, dT$$

2. **Melting.** With the surface held at 0 °C, the heat flux is constant and the radius shrinks at a steady rate, giving

   $$t_2 = \frac{R \rho L}{h (T_r - 273.15) + \varepsilon \sigma (T_r^4 - 273.15^4)}$$

The convection coefficient $h$ scales with the temperature difference to the 1/4 power, as for natural convection.

## Usage

```bash
python ice_melt_time.py
```

```
Initial radius of the ice sphere (m): 0.05
Freezer temperature (C): -18
Room temperature (C): 22
Time to melt: 13 h 34 min 26.19 s
```
