# run_gallery.py
import sys
import matplotlib.pyplot as plt
from config import Config

# 지금까지 만든 모듈들 import
# (파일이 없으면 해당 라인은 주석 처리하거나 건너뛰세요)
try:
    from models.vsg_model import swing_equation
    from models.hybrid_system import system_dynamics
    from models.avm_system import voltage_dynamics
    from models.gfl_model import get_solar_power
    from utils.visualizer import plot_hybrid_results, plot_voltage_control
    from models.stability_analyzer import plot_stability_region
    from models.eigen_analysis import plot_root_locus
    from models.pareto_analysis import plot_pareto_front
    from scipy.integrate import odeint
    import numpy as np
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all previous steps (files) are created correctly.")
    sys.exit()


def run_time_domain(cfg):
    print("Running Time Domain Simulation (Hybrid)...")
    P_vsg_initial = cfg.P_load_total - cfg.P_solar_initial
    P_max = cfg.V_vsg * cfg.V_grid / cfg.X_line
    delta_0 = np.arcsin(P_vsg_initial / P_max)
    y0 = [delta_0, cfg.Omega_0]
    t = np.linspace(cfg.t_start, cfg.t_end, cfg.steps)
    sol = odeint(system_dynamics, y0, t, args=(cfg,))
    solar = np.array([get_solar_power(time, cfg) for time in t])
    plot_hybrid_results(t, sol, solar, cfg)


def run_voltage_domain(cfg):
    print("Running Voltage Domain Simulation (AVR)...")
    y0 = [0.1, cfg.Omega_0, 1.0]  # delta, omega, V
    t = np.linspace(cfg.t_start, cfg.t_end, cfg.steps)
    sol = odeint(voltage_dynamics, y0, t, args=(cfg,))
    plot_voltage_control(t, sol, cfg)


def main_menu():
    cfg = Config()

    while True:
        print("\n" + "=" * 40)
        print("   VSG THESIS REPRODUCTION GALLERY")
        print("=" * 40)
        print("1. [Time Domain] Hybrid System (Solar Drop)")
        print("2. [Time Domain] Voltage Control (AVR)")
        print("3. [Analysis] P-X Stability Region Map")
        print("4. [Analysis] Root Locus (Eigenvalues)")
        print("5. [Optimization] Pareto Front (Cost-Benefit)")
        print("0. Exit")
        print("-" * 40)

        choice = input("Select Graph (0-5): ")

        if choice == "1":
            run_time_domain(cfg)
        elif choice == "2":
            run_voltage_domain(cfg)
        elif choice == "3":
            plot_stability_region(cfg)
        elif choice == "4":
            plot_root_locus(cfg)
        elif choice == "5":
            plot_pareto_front(cfg)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main_menu()
