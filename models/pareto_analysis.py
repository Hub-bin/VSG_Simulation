# models/pareto_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from models.hybrid_system import system_dynamics


def plot_pareto_front(config):
    print("--- Generating Pareto Front Curve ---")

    # 테스트할 관성 상수(H) 범위: 1.0 ~ 10.0
    h_values = np.linspace(1.0, 10.0, 20)
    nadir_values = []

    # 시뮬레이션 반복 수행
    for h in h_values:
        original_h = config.H
        config.H = h

        # 초기 상태 및 솔버 실행
        P_vsg_initial = config.P_load_total - config.P_solar_initial
        P_max = config.V_vsg * config.V_grid / config.X_line
        delta_0 = np.arcsin(P_vsg_initial / P_max)
        y0 = [delta_0, config.Omega_0]
        t = np.linspace(config.t_start, config.t_end, config.steps)

        sol = odeint(system_dynamics, y0, t, args=(config,))

        # 주파수 최저점(Nadir) 기록
        freq = sol[:, 1] / (2 * np.pi)
        nadir_values.append(np.min(freq))

        config.H = original_h  # 복구

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(h_values, nadir_values, "bo-", linewidth=2, markersize=8)

    # 안전 기준선 표시 (예: 59.2Hz)
    plt.axhline(y=59.2, color="r", linestyle="--", label="Safety Limit (59.2Hz)")

    plt.title("Pareto Front: Cost (Inertia) vs Performance (Frequency)", fontsize=16)
    plt.xlabel("Battery Inertia H [s] (Configured Cost)", fontsize=14)
    plt.ylabel("Frequency Nadir [Hz] (Safety Performance)", fontsize=14)
    plt.grid(True)
    plt.legend()

    # 최적점 부근 강조
    plt.annotate(
        "Diminishing Returns\n(More H gives less gain)",
        xy=(8, 59.6),
        xytext=(5, 59.3),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    print("--- Pareto Front Generated ---")
    plt.show()
