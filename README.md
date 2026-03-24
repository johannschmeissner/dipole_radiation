# Dipole Radiation Visualizer

An interactive Python tool for visualizing electromagnetic field vectors around an oscillating electric dipole. The simulation covers the **Near-field**, **Induction zone**, and **Far-field (Radiation zone)**.

## 🚀 Features
- **Dynamic Simulation**: Real-time E and H field calculation.
- **Interactive UI**: Drag-and-drop sliders for Charge ($q$) and Frequency ($\omega$).
- **Physics Data**: Real-time calculation of wavelength ($\lambda$) and radiation intensity ($P$).
- **Radiation Pattern**: Dynamic polar plot showing $I \sim \sin^2 \theta$ distribution.
- **Analysis Tool**: Hover over any point to get local $E$ and $H$ field values.
- **Dual Themes**: Light and Dark modes for better visibility.

## 📚 Theory
The program solves the full Maxwell-derived equations for a Hertzian dipole. Unlike the far-field approximation, this visualizer includes $1/r^2$ and $1/r^3$ terms to accurately show field behavior near the source.

### Key Approximations:
- **Hertzian Dipole**: The source is a point-like oscillating dipole $\mathbf{p}(t) = \mathbf{p}_0 e^{-i\omega t}$.
- **Visualization Scale**: The speed of light is scaled to $100 \, \text{m/s}$ for fluid wave propagation visibility on screen.
- **Symmetry**: The field is calculated in the $XY$ plane, where $\mathbf{H}$ is always perpendicular to the screen.

## 🛠 Installation & Usage
1. Ensure you have Python 3.x installed.
2. Install dependencies:
   ```bash
   pip install pygame numpy
