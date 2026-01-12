# step12_detailed_vsg.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


# ==========================================
# 1. 상세 모델 설정 (Detailed Configuration)
# ==========================================
class DetailedConfig:
    def __init__(self):
        # 시스템 기본
        self.w_base = 2 * np.pi * 60.0
        self.S_base = 1e6  # 1MVA 기준

        # 외부 루프 (VSG Power Loop)
        self.J = 0.5  # 관성 (Inertia, H와 유사)
        self.D = 10.0  # 감쇠 (Damping)
        self.P_ref = 0.5
        self.Q_ref = 0.0
        self.K_q = 0.0  # Q-Droop (간소화를 위해 일단 0)
        self.V_ref = 1.0

        # 내부 루프 1: 전압 제어기 (PI)
        self.Kpv = 0.5
        self.Kiv = 50.0

        # 내부 루프 2: 전류 제어기 (PI)
        self.Kpc = 0.5
        self.Kic = 100.0

        # 물리적 하드웨어 (LC 필터 및 선로)
        # 단위: p.u. (per unit)
        self.R_f = 0.01  # 필터 저항
        self.L_f = 0.05  # 필터 인덕턴스 (Internal)
        self.C_f = 0.05  # 필터 커패시턴스

        self.R_g = 0.02  # 전력망 선로 저항
        self.L_g = 0.2  # 전력망 선로 인덕턴스 (Weak Grid)

        self.V_grid_mag = 1.0  # 무한모선 전압 크기


# ==========================================
# 2. 미분 방정식 (12-Order State Space)
# ==========================================
def detailed_dynamics(states, t, cfg):
    # --- State Unpacking (12개 변수) ---
    # 1. VSG Mechanics
    delta = states[0]  # 위상각
    omega = states[1]  # 각속도

    # 2. PI Integrators (dq frame)
    int_vd = states[2]  # 전압제어 d축 적분
    int_vq = states[3]  # 전압제어 q축 적분
    int_id = states[4]  # 전류제어 d축 적분
    int_iq = states[5]  # 전류제어 q축 적분

    # 3. Physical Filter States (dq frame)
    i_Ld = states[6]  # 인버터 전류 d
    i_Lq = states[7]  # 인버터 전류 q
    v_od = states[8]  # 커패시터 전압 d (출력전압)
    v_oq = states[9]  # 커패시터 전압 q (출력전압)
    i_gd = states[10]  # 전력망 전류 d
    i_gq = states[11]  # 전력망 전류 q

    # --- A. 좌표계 변환 및 측정 ---
    # 전력망 전압 (Grid Frame -> Inverter DQ Frame 변환)
    # Grid 전압은 고정되어 있지만, 인버터가 delta만큼 회전하고 있음
    # Vg_d = Vg * cos(-delta), Vg_q = Vg * sin(-delta)
    v_gd = cfg.V_grid_mag * np.cos(-delta)
    v_gq = cfg.V_grid_mag * np.sin(-delta)

    # 출력 유효전력 P, 무효전력 Q 계산
    P_calc = v_od * i_gd + v_oq * i_gq
    Q_calc = v_oq * i_gd - v_od * i_gq

    # --- B. 가장 바깥쪽 루프 (Swing Equation) ---
    # P_ref 입력 (0.5초에 부하 투입)
    P_m = cfg.P_ref if t > 0.5 else 0.0

    # d(delta)/dt = omega - w_base
    d_delta = omega - cfg.w_base

    # J * d(omega)/dt ...
    d_omega = (1 / cfg.J) * (P_m - P_calc - cfg.D * (omega - cfg.w_base))

    # --- C. 전압 제어 루프 (Voltage Control) ---
    # Reference Generation (Local DQ frame)
    # d축을 전압 크기로 잡음 (V_ref), q축은 0
    v_od_ref = cfg.V_ref - cfg.K_q * (Q_calc - cfg.Q_ref)
    v_oq_ref = 0.0

    # Error Calculation
    err_vd = v_od_ref - v_od
    err_vq = v_oq_ref - v_oq

    # PI Output (Reference Current)
    # Decoupling Term: -w * C * v_q (Cross coupling cancellation)
    i_Ld_ref = (cfg.Kpv * err_vd + int_vd) - (omega * cfg.C_f * v_oq)
    i_Lq_ref = (cfg.Kpv * err_vq + int_vq) + (omega * cfg.C_f * v_od)

    # Integrator Dynamics
    d_int_vd = cfg.Kiv * err_vd
    d_int_vq = cfg.Kiv * err_vq

    # --- D. 전류 제어 루프 (Current Control) ---
    # Error
    err_id = i_Ld_ref - i_Ld
    err_iq = i_Lq_ref - i_Lq

    # PI Output (Inverter Modulation Voltage)
    # Decoupling + Feedforward
    v_inv_d = (cfg.Kpc * err_id + int_id) - (omega * cfg.L_f * i_Lq) + v_od
    v_inv_q = (cfg.Kpc * err_iq + int_iq) + (omega * cfg.L_f * i_Ld) + v_oq

    # Integrator Dynamics
    d_int_id = cfg.Kic * err_id
    d_int_iq = cfg.Kic * err_iq

    # --- E. LC 필터 및 선로 물리 모델 (Physical Plant) ---
    # 1. 인버터 전류 (L_f) dynamics
    # L di/dt = V_in - V_out - R*i - CrossCoupling
    d_iLd = (1 / cfg.L_f) * (v_inv_d - v_od - cfg.R_f * i_Ld + omega * cfg.L_f * i_Lq)
    d_iLq = (1 / cfg.L_f) * (v_inv_q - v_oq - cfg.R_f * i_Lq - omega * cfg.L_f * i_Ld)

    # 2. 커패시터 전압 (C_f) dynamics
    # C dv/dt = i_in - i_out - CrossCoupling
    d_vod = (1 / cfg.C_f) * (i_Ld - i_gd + omega * cfg.C_f * v_oq)
    d_voq = (1 / cfg.C_f) * (i_Lq - i_gq - omega * cfg.C_f * v_od)

    # 3. 전력망 전류 (Line L_g) dynamics
    # L_g di_g/dt = V_out - V_grid - R_g*i_g - CrossCoupling
    d_igd = (1 / cfg.L_g) * (v_od - v_gd - cfg.R_g * i_gd + omega * cfg.L_g * i_gq)
    d_igq = (1 / cfg.L_g) * (v_oq - v_gq - cfg.R_g * i_gq - omega * cfg.L_g * i_gd)

    return [
        d_delta,
        d_omega,
        d_int_vd,
        d_int_vq,
        d_int_id,
        d_int_iq,
        d_iLd,
        d_iLq,
        d_vod,
        d_voq,
        d_igd,
        d_igq,
    ]


# ==========================================
# 3. 메인 실행 및 시각화
# ==========================================
def main():
    print("=== Step 12: Detailed Model Simulation (Inner Loops) ===")
    cfg = DetailedConfig()

    # 초기 조건 (0에서 시작 - Black Start)
    # 시스템이 0에서 전압을 확 올리는 과도 응답을 관찰
    y0 = np.zeros(12)
    y0[1] = cfg.w_base  # 주파수는 60Hz에서 시작

    t = np.linspace(0, 1.5, 3000)  # 1.5초간 시뮬레이션

    print("Solving 12-order differential equations...")
    sol = odeint(detailed_dynamics, y0, t, args=(cfg,))
    print("Simulation Finished.")

    # 결과 추출
    omega = sol[:, 1]
    v_od = sol[:, 8]
    v_oq = sol[:, 9]
    i_gd = sol[:, 10]
    i_gq = sol[:, 11]

    # 유효전력 계산
    P_out = v_od * i_gd + v_oq * i_gq

    # 전압 크기 (RMS 개념)
    V_mag = np.sqrt(v_od**2 + v_oq**2)

    # --- 그래프 ---
    plt.figure(figsize=(12, 10))

    # 1. 전압 형성 과정 (Black Start)
    plt.subplot(3, 1, 1)
    plt.plot(t, V_mag, "b", linewidth=2, label="Voltage Magnitude (v_d)")
    plt.plot(t, v_oq, "g--", alpha=0.5, label="v_q (Should be 0)")
    plt.title("1. Voltage Build-up (Inner Loop Response)")
    plt.ylabel("Voltage [p.u.]")
    plt.grid(True)
    plt.legend()

    # 2. 유효 전력 응답
    plt.subplot(3, 1, 2)
    plt.plot(t, P_out, "r", linewidth=2, label="Active Power Output")
    plt.axvline(x=0.5, color="k", linestyle="--", label="Load Step (0.5s)")
    plt.title("2. Active Power Response (Outer Loop Response)")
    plt.ylabel("Power [p.u.]")
    plt.grid(True)
    plt.legend()

    # 3. 주파수 응답
    plt.subplot(3, 1, 3)
    freq_Hz = omega / (2 * np.pi)
    plt.plot(t, freq_Hz, "k", linewidth=2)
    plt.title("3. Frequency Response (Virtual Inertia)")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
