# Grid-Forming Battery (VSG) Simulation for Power System Stability

This project simulates a **Virtual Synchronous Generator (VSG)** based grid-forming battery system. It implements the key concepts from the Ph.D. thesis *"Empowering Grid-Forming Battery for Future Power System Stability"* (Yunda Xu, UQ, 2024).

## Project Overview
This simulation analyzes how VSG control enhances power system stability under high renewable penetration and weak grid conditions.

### Key Features
1.  **Swing Equation Modeling:** Simulates frequency dynamics using virtual inertia ($H$) and damping ($D$).
2.  **Weak Grid Analysis:** Compares stability between strong vs. weak grid connections (High Impedance).
3.  **Hybrid Operation:** Co-simulation of Grid-Following (GFL) Solar PV and Grid-Forming (GFM) Battery.
4.  **Parameter Optimization:** Automatically finds the minimum required inertia ($H$) to maintain safety thresholds (e.g., nadir > 59.2Hz).

## File Structure
- `main.py`: Main entry point for running simulations.
- `config.py`: Configuration for system parameters (Grid, VSG, Solar).
- `models/`:
    - `vsg_model.py`: Basic swing equation logic.
    - `gfl_model.py`: Solar PV profile generation.
    - `hybrid_system.py`: Combined dynamics (VSG + GFL + Load).
    - `optimizer.py`: Binary search algorithm for sizing.
- `utils/`:
    - `visualizer.py`: Plotting tools for frequency and power response.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt