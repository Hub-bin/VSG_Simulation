# main.py
import numpy as np
from scipy.integrate import odeint
from config import Config
from models.hybrid_system import system_dynamics
from models.gfl_model import get_solar_power
from models.optimizer import find_optimal_inertia  # 추가됨
from utils.visualizer import plot_hybrid_results


def run_simulation(cfg):
    """현재 설정된 cfg로 시뮬레이션 실행"""
    P_vsg_initial = cfg.P_load_total - cfg.P_solar_initial
    P_max = cfg.V_vsg * cfg.V_grid / cfg.X_line
    delta_0 = np.arcsin(P_vsg_initial / P_max)
    y0 = [delta_0, cfg.Omega_0]
    t = np.linspace(cfg.t_start, cfg.t_end, cfg.steps)
    sol = odeint(system_dynamics, y0, t, args=(cfg,))
    return t, sol


def main():
    print("=== VSG Simulation Step 5: Optimal Sizing (Optimization) ===")
    cfg = Config()

    # 1. 최적화 수행: 안전 한계(59.2Hz)를 지키는 최소 H 찾기
    target_freq_limit = 59.2
    optimal_H = find_optimal_inertia(cfg, safety_threshold=target_freq_limit)

    if optimal_H is None:
        print("Optimization Failed: Could not find valid H in range.")
        return

    # 2. 찾은 최적값 적용
    print(f"\nApplying Optimal Inertia H = {optimal_H:.2f} to simulation...")
    cfg.H = optimal_H

    # 3. 최적 결과 시뮬레이션
    t, sol = run_simulation(cfg)

    # 4. 결과 시각화
    solar_profile = np.array([get_solar_power(time, cfg) for time in t])
    plot_hybrid_results(t, sol, solar_profile, cfg)

    print(f"\n=== Result Analysis ===")
    print(f"Design Requirement: Frequency must stay above {target_freq_limit} Hz")
    print(
        f"Optimized Result:   Minimum Frequency was {np.min(sol[:, 1] / (2 * np.pi)):.4f} Hz"
    )
    print(
        f"Conclusion: We saved battery cost by using H={optimal_H:.2f} instead of a larger random value."
    )


if __name__ == "__main__":
    main()
