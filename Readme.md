# Mathematical Curve Visualizer

The Mathematical Curve Visualizer is an interactive computer graphics project that allows users to visualize and explore various mathematical curves—including circles, parabolas, ellipses, and hyperbolas—in real time. Built using Python, Pygame, and PyOpenGL, the project demonstrates fundamental computer graphics concepts such as viewport management, orthographic projections, anti-aliasing, and immediate mode rendering.

## Features

- **Real-Time Rendering:**  
  Dynamically render curves as users adjust parameters.

- **Multiple Curves:**  
  Visualize different types of curves:
  - **Circle:** Adjust the radius.
  - **Parabola:** Modify quadratic coefficients.
  - **Ellipse:** Change the x- and y-axis scales.
  - **Hyperbola:** Explore both branches using hyperbolic functions.

- **Interactive GUI:**  
  - **Buttons:** Easily switch between curve types.
  - **Sliders:** Adjust curve parameters (e.g., radius, coefficients, axes lengths).
  - **Information Panel:** Displays the corresponding mathematical equation and facts about the current curve.

- **Computer Graphics Techniques:**  
  - Uses multiple viewports and custom orthographic projections to separate the GUI and the visualization area.
  - Anti-aliasing and line smoothing for crisp, clean curve rendering.

## Installation

### Prerequisites

- **Python 3.x**
- **Pygame**
- **PyOpenGL**

You can install the required packages using `pip`:

```bash
pip install pygame PyOpenGL