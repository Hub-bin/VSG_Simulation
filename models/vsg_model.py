# models/vsg_model.py
import numpy as np


def swing_equation(y, t, config):
    """
    VSG의 동요 방정식 (Swing Equation)
    y: 상태 변수 벡터 [delta (rad), omega (rad/s)]
    t: 현재 시간
    config: 파라미터 객체
    """
    delta, omega = y

    # 1. 전기적 출력 계산 (P_elec)
    # P = (V1 * V2 / X) * sin(delta)
    P_out = (config.V_vsg * config.V_grid / config.X_line) * np.sin(delta)

    # 2. 기계적 입력 계산 (P_mech) - 이벤트 반영
    # 외란 발생(event_time) 이후에는 부하가 증가하여
    # 상대적으로 발전원(VSG) 입장에서 출력이 부족한 상황 모사
    if t >= config.event_time:
        P_m = config.P_ref - config.P_load_step
    else:
        P_m = config.P_ref

    # 3. 미분 방정식 (Dynamics)
    # d(delta)/dt = omega - Omega_0
    d_delta_dt = omega - config.Omega_0

    # J * d(omega)/dt = P_m - P_out - D * (omega - Omega_0)
    # 정규화된 식: 2H * d(omega)/dt ...
    # 논문의 식을 따름
    d_omega_dt = (
        (1 / (2 * config.H))
        * (P_m - P_out - config.D * (omega - config.Omega_0) / config.Omega_0)
        * config.Omega_0
    )

    return [d_delta_dt, d_omega_dt]
