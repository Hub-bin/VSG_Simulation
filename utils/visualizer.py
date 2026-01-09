# utils/visualizer.py
import matplotlib.pyplot as plt
import numpy as np


def plot_hybrid_results(t, result, solar_profile, config):
    delta_res = result[:, 0]
    omega_res = result[:, 1]
    freq_res = omega_res / (2 * np.pi)

    # VSG 출력 전력 계산
    vsg_power = (config.V_vsg * config.V_grid / config.X_line) * np.sin(delta_res)

    plt.figure(figsize=(12, 12))

    # 1. 태양광 발전량 (GFL)
    plt.subplot(3, 1, 1)
    plt.plot(t, solar_profile, "orange", linewidth=2, label="Solar (GFL) Power")
    plt.ylabel("Power [p.u.]")
    plt.title("[Scenario] Solar Power Drop (Cloud Passing)", fontsize=14)
    plt.grid(True)
    plt.legend(loc="upper right")

    # 2. 주파수 응답 (System Frequency)
    plt.subplot(3, 1, 2)
    plt.plot(t, freq_res, "b", linewidth=2, label="Grid Frequency (VSG Controlled)")
    plt.axvline(x=config.event_time, color="r", linestyle="--", alpha=0.5)
    plt.ylabel("Frequency [Hz]")
    plt.title("System Frequency Response", fontsize=14)
    plt.grid(True)
    plt.legend(loc="upper right")

    # 3. VSG 출력 전력 (VSG Response)
    plt.subplot(3, 1, 3)
    plt.plot(t, vsg_power, "g", linewidth=2, label="VSG Output Power")
    plt.plot(
        t, config.P_load_total - solar_profile, "k:", label="Required VSG Power (Ideal)"
    )
    plt.ylabel("Power [p.u.]")
    plt.xlabel("Time [s]")
    plt.title("VSG Inertial Response (Compensating for Solar Loss)", fontsize=14)
    plt.grid(True)
    plt.legend(loc="upper right")

    plt.tight_layout()
    plt.show()


def plot_parametric_sweep(t, results_dict, config):
    """
    파라미터 변화에 따른 비교 그래프 그리기
    results_dict: { 'H=3.0': result_array, ... }
    """
    plt.figure(figsize=(12, 10))

    # 1. 주파수 비교 (가장 중요)
    plt.subplot(2, 1, 1)
    for label, result in results_dict.items():
        omega_res = result[:, 1]
        freq_res = omega_res / (2 * np.pi)

        # 최저 주파수(Nadir) 표시
        min_freq = np.min(freq_res)

        plt.plot(t, freq_res, linewidth=2, label=f"{label} (Min: {min_freq:.4f} Hz)")

    plt.axvline(
        x=config.event_time, color="r", linestyle="--", alpha=0.5, label="Solar Drop"
    )
    plt.axhline(y=59.5, color="k", linestyle=":", label="Safety Threshold (59.5Hz)")
    plt.title("Effect of Inertia (H) on Frequency Stability", fontsize=14)
    plt.ylabel("Frequency [Hz]", fontsize=12)
    plt.legend(loc="lower right")
    plt.grid(True)

    # 2. VSG 출력 전력 비교
    plt.subplot(2, 1, 2)
    for label, result in results_dict.items():
        delta_res = result[:, 0]
        vsg_power = (config.V_vsg * config.V_grid / config.X_line) * np.sin(delta_res)
        plt.plot(t, vsg_power, linewidth=2, label=label)

    plt.title("VSG Active Power Response", fontsize=14)
    plt.xlabel("Time [s]", fontsize=12)
    plt.ylabel("Power [p.u.]", fontsize=12)
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()
