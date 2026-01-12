# standalone_verification.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


# ==========================================
# 1. 설정 및 파라미터 (Configuration)
# ==========================================
class Config:
    def __init__(self):
        self.F_base = 60.0
        self.Omega_0 = 2 * np.pi * self.F_base

        # --- 핵심: 물리적 여유 확보 ---
        # X=1.2일 때 P_max는 약 0.83입니다.
        # P_ref를 0.8로 하면 너무 위험하므로 0.5로 낮춥니다.
        self.X_line = 1.2  # Weak Grid
        self.P_ref = 0.5  # [수정됨] 0.8 -> 0.5 (Safety Margin 확보)

        self.V_grid = 1.0
        self.H = 3.0  # 낮은 관성 (진동 유발)
        self.D = 5.0

        # 전압 제어 파라미터
        self.V_ref_base = 1.0
        self.K_q = 0.5
        self.T_v = 0.1

        # 제안 기법 파라미터 (NVR)
        self.use_proposed_control = False
        self.K_nvr = 0.1  # 적절한 게인 값


# ==========================================
# 2. 동적 모델 (Dynamics Model)
# ==========================================
def system_dynamics(y, t, cfg):
    delta, omega, V_vsg = y

    # 외란: 1.0초에 부하 투입 (Step Change)
    P_mech = cfg.P_ref if t >= 1.0 else 0.0

    # 전기적 출력 계산
    # P = (V*V/X) * sin(delta)
    # Q = (V*V/X) * (1 - cos(delta)) approx
    P_out = (V_vsg * cfg.V_grid / cfg.X_line) * np.sin(delta)
    Q_out = (V_vsg**2 / cfg.X_line) - (V_vsg * cfg.V_grid / cfg.X_line) * np.cos(delta)

    # 1. 주파수 미분방정식 (Swing Eq)
    d_delta_dt = omega - cfg.Omega_0
    d_omega_dt = (
        (1 / (2 * cfg.H))
        * (P_mech - P_out - cfg.D * (omega - cfg.Omega_0) / cfg.Omega_0)
        * cfg.Omega_0
    )

    # 2. 전압 미분방정식 (AVR)
    V_target = cfg.V_ref_base - cfg.K_q * Q_out

    # [논문 제안 기법: NVR]
    if cfg.use_proposed_control:
        # 주파수 진동을 전압으로 상쇄
        raw_signal = cfg.K_nvr * (omega - cfg.Omega_0)
        # 리미터: +/- 0.05 p.u.로 제한 (안전장치)
        stabilizing_signal = np.clip(raw_signal, -0.05, 0.05)
        V_target += stabilizing_signal

    d_v_dt = (V_target - V_vsg) / cfg.T_v

    return [d_delta_dt, d_omega_dt, d_v_dt]


# ==========================================
# 3. 메인 실행 및 시각화
# ==========================================
def main():
    print("=== Standalone Verification Started ===")
    cfg = Config()
    t = np.linspace(0, 10, 1000)
    y0 = [0.0, cfg.Omega_0, 1.0]

    # Case 1: 기존 제어 (NVR OFF)
    print("Running Case 1: Conventional (NVR OFF)...")
    cfg.use_proposed_control = False
    sol1 = odeint(system_dynamics, y0, t, args=(cfg,))

    # Case 2: 제안 제어 (NVR ON)
    print("Running Case 2: Proposed (NVR ON)...")
    cfg.use_proposed_control = True
    sol2 = odeint(system_dynamics, y0, t, args=(cfg,))

    # 그래프 그리기
    plt.figure(figsize=(12, 8))

    # 유효 전력 (P)
    plt.subplot(2, 1, 1)
    P1 = (sol1[:, 2] * cfg.V_grid / cfg.X_line) * np.sin(sol1[:, 0])
    P2 = (sol2[:, 2] * cfg.V_grid / cfg.X_line) * np.sin(sol2[:, 0])

    plt.plot(t, P1, "r--", alpha=0.6, label="Conventional (Oscillating)")
    plt.plot(t, P2, "b-", linewidth=2, label="Proposed NVR (Damped)")
    plt.axvline(x=1.0, color="k", linestyle=":", label="Event")
    plt.title(
        f"Effect of NVR Control (Weak Grid X={cfg.X_line}, P={cfg.P_ref})", fontsize=14
    )
    plt.ylabel("Active Power [p.u.]")
    plt.legend(loc="upper right")
    plt.grid(True)

    # 전압 (V)
    plt.subplot(2, 1, 2)
    plt.plot(t, sol1[:, 2], "r--", alpha=0.6, label="Conventional")
    plt.plot(t, sol2[:, 2], "b-", linewidth=2, label="Proposed NVR")
    plt.title("Voltage Stability", fontsize=14)
    plt.ylabel("Voltage [p.u.]")
    plt.xlabel("Time [s]")
    plt.legend(loc="upper right")
    plt.grid(True)

    plt.tight_layout()
    plt.show()
    print("=== Done ===")


if __name__ == "__main__":
    main()
