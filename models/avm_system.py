import numpy as np


def voltage_dynamics(y, t, config):
    """
    VSG의 전압 및 주파수 동역학 모델 (AVR + Swing Equation)
    상태 변수 y: [delta (위상각), omega (각속도), V_vsg (배터리 전압)]
    """
    delta, omega, V_vsg = y

    # 1. 전력망 전압 설정 (시나리오에 따른 전압 변화 반영)
    if t >= config.event_time:
        V_grid = config.V_grid_fault
    else:
        V_grid = config.V_grid_normal

    # 2. 전기적 출력 계산 (P, Q)
    # P_out = (V1*V2/X) * sin(delta)
    P_out = (V_vsg * V_grid / config.X_line) * np.sin(delta)

    # Q_out = (V1^2/X) - (V1*V2/X) * cos(delta)
    Q_out = (V_vsg**2 / config.X_line) - (V_vsg * V_grid / config.X_line) * np.cos(
        delta
    )

    # 3. [Dynamics 1] 주파수 동역학 (Swing Equation)
    # 기계적 입력(P_ref) 설정
    P_mech = config.P_ref

    d_delta_dt = omega - config.Omega_0

    d_omega_dt = (
        (1 / (2 * config.H))
        * (P_mech - P_out - config.D * (omega - config.Omega_0) / config.Omega_0)
        * config.Omega_0
    )

    # 4. [Dynamics 2] 전압 동역학 (AVR & Q-V Droop)
    # 기본 목표 전압 계산 (Droop Control 적용)
    # V_target = V_ref - Kq * Q
    V_target = config.V_ref_base - config.K_q * Q_out

    # --- [논문 제안 기법: Proposed NVR Control] ---
    if config.use_proposed_control:
        # 주파수 흔들림(omega - omega0)을 감지하여 전압을 조절함으로써 진동 억제
        raw_signal = config.K_nvr * (omega - config.Omega_0)

        # [중요] 안전장치 (Saturation Limiter)
        # 제어 신호가 +/- 0.1 p.u.를 넘지 못하도록 제한하여 폭주 방지
        stabilizing_signal = np.clip(raw_signal, -0.1, 0.1)

        V_target += stabilizing_signal

    # AVR 지연 특성 (1차 지연 미분 방정식)
    # dV/dt = (Target - Current) / Time_Constant
    d_v_dt = (V_target - V_vsg) / config.T_v

    return [d_delta_dt, d_omega_dt, d_v_dt]
