# main.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import os
from config import Config
from models.avm_system import voltage_dynamics


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def run_simulation(cfg, label):
    # 초기 상태
    y0 = [0.0, cfg.Omega_0, 1.0]  # delta, omega, V_vsg
    t = np.linspace(cfg.t_start, cfg.t_end, cfg.steps)

    # 솔버 실행
    sol = odeint(voltage_dynamics, y0, t, args=(cfg,))
    return t, sol


def analyze_and_log(t, sol, cfg, label):
    """
    시뮬레이션 결과를 분석하여 로그를 남기고,
    제어기 내부 신호(NVR 등)를 역산하여 반환함
    """
    delta = sol[:, 0]
    omega = sol[:, 1]
    V_vsg = sol[:, 2]

    # 1. 물리량 역산 (P, Q)
    # 시뮬레이션 중 V_grid는 이벤트 시간에 따라 변함
    V_grid_arr = np.where(t >= cfg.event_time, cfg.V_grid_fault, cfg.V_grid_normal)

    P = (V_vsg * V_grid_arr / cfg.X_line) * np.sin(delta)
    Q = (V_vsg**2 / cfg.X_line) - (V_vsg * V_grid_arr / cfg.X_line) * np.cos(delta)

    # 2. 제어 신호 역산 (NVR Signal 확인용)
    # NVR 신호 = K_nvr * (omega - Omega_0)
    # 이 값이 너무 크면 시스템이 발산함
    freq_deviation = omega - cfg.Omega_0
    nvr_signal = np.zeros_like(freq_deviation)

    if cfg.use_proposed_control:
        nvr_signal = cfg.K_nvr * freq_deviation

    # 3. 로그 출력 (터미널)
    print(f"\n[DEBUG LOG] --- {label} ---")
    print(f"  > Voltage Range : Min {np.min(V_vsg):.4f} ~ Max {np.max(V_vsg):.4f} p.u.")
    print(f"  > Active Power  : Min {np.min(P):.4f} ~ Max {np.max(P):.4f} p.u.")
    print(f"  > Freq Deviat.  : Max Abs {np.max(np.abs(freq_deviation)):.4f} rad/s")

    if cfg.use_proposed_control:
        print(
            f"  > NVR Signal    : Max Abs {np.max(np.abs(nvr_signal)):.4f} p.u. (Control Effort)"
        )
        if np.max(np.abs(nvr_signal)) > 0.2:
            print(
                "  [WARNING] NVR Control signal is too strong! (> 0.2 p.u.) Check K_nvr gain."
            )

    return P, Q, V_vsg, nvr_signal


def main():
    print("=== VSG Simulation: Debugging Mode ===")

    # 결과 저장 폴더 생성
    ensure_dir("results")

    cfg = Config()

    # [디버깅 포인트 1] X_line이 너무 크면 기본 제어도 발산할 수 있음
    cfg.X_line = 1.2

    # --- Case 1: 기존 제어 ---
    print("\nRunning Case 1: Conventional...")
    cfg.use_proposed_control = False
    t1, sol1 = run_simulation(cfg, "Conventional")
    P1, Q1, V1, NVR1 = analyze_and_log(t1, sol1, cfg, "Conventional")

    # --- Case 2: 제안 제어 ---
    print("\nRunning Case 2: Proposed NVR...")
    cfg.use_proposed_control = True
    t2, sol2 = run_simulation(cfg, "Proposed")
    P2, Q2, V2, NVR2 = analyze_and_log(t2, sol2, cfg, "Proposed")

    # --- 그래프 그리기 ---
    plt.figure(figsize=(12, 12))

    # 1. 유효 전력 (P)
    plt.subplot(3, 1, 1)
    plt.plot(t1, P1, "r--", alpha=0.7, label="Conventional")
    plt.plot(t2, P2, "b-", linewidth=2, label="Proposed NVR")
    plt.axvline(x=cfg.event_time, color="k", linestyle=":")
    plt.title("Active Power (P)")
    plt.ylabel("Power [p.u.]")
    plt.legend()
    plt.grid(True)

    # 2. 전압 (V)
    plt.subplot(3, 1, 2)
    plt.plot(t1, V1, "r--", alpha=0.7, label="Conventional")
    plt.plot(t2, V2, "b-", linewidth=2, label="Proposed NVR")
    plt.title("Voltage Stability (V)")
    plt.ylabel("Voltage [p.u.]")
    plt.legend()
    plt.grid(True)

    # 3. 디버깅용: NVR 제어 신호
    # 파란색 선이 이상했던 이유가 여기서 밝혀질 수 있음
    plt.subplot(3, 1, 3)
    plt.plot(t2, NVR2, "g", label="NVR Control Signal (Proposed Only)")
    plt.title("Debug: NVR Control Signal Injection")
    plt.ylabel("V_injection [p.u.]")
    plt.xlabel("Time [s]")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    # 파일 저장
    save_path = "results/debug_result.png"
    plt.savefig(save_path, dpi=300)
    print(f"\n[INFO] Graph saved to: {save_path}")

    plt.show()


if __name__ == "__main__":
    main()
