# models/avm_system.py
import numpy as np


def voltage_dynamics(y, t, config):
    """
    3차 상태 방정식: [delta, omega, V_vsg]
    """
    delta, omega, V_vsg = y

    # 1. 시나리오: 전력망 전압(V_grid) 변화
    # 2초 후에 전력망 전압이 뚝 떨어짐 (Grid Fault)
    if t >= config.event_time:
        V_grid = config.V_grid_fault
    else:
        V_grid = config.V_grid_normal

    # 2. 출력 전력 계산 (P, Q)
    # P_out = (V1*V2/X) * sin(delta)
    # Q_out = (V1^2/X) - (V1*V2/X) * cos(delta)  (송전단 기준 근사식)
    P_out = (V_vsg * V_grid / config.X_line) * np.sin(delta)
    Q_out = (V_vsg**2 / config.X_line) - (V_vsg * V_grid / config.X_line) * np.cos(
        delta
    )

    # --- [Dynamics 1] 유효 전력 (주파수) ---
    # P_mech는 일정하다고 가정 (Voltage 테스트 집중을 위해 Solar 제외)
    d_delta_dt = omega - config.Omega_0
    d_omega_dt = (
        (1 / (2 * config.H))
        * (config.P_ref - P_out - config.D * (omega - config.Omega_0) / config.Omega_0)
        * config.Omega_0
    )

    # --- [Dynamics 2] 무효 전력 (전압) [신규] ---
    # 목표 전압(V_target) = 기준전압 - 드룹계수 * (현재Q - 기준Q)
    # 기준 Q는 0이라고 가정
    V_target = config.V_ref_base - config.K_q * Q_out

    # 1차 지연 미분 방정식 (AVR 동작)
    # dV/dt = (목표값 - 현재값) / 시상수
    d_v_dt = (V_target - V_vsg) / config.T_v

    return [d_delta_dt, d_omega_dt, d_v_dt]
