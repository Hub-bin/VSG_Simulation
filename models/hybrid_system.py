# models/hybrid_system.py
import numpy as np
from models.gfl_model import get_solar_power


def system_dynamics(y, t, config):
    """
    하이브리드 시스템 (VSG + GFL + Load) 동역학
    """
    delta, omega = y

    # 1. 태양광(GFL) 발전량 확인
    P_solar = get_solar_power(t, config)

    # 2. 전력망 상황 계산
    # 부하(Load)는 일정하다고 가정했을 때,
    # VSG가 감당해야 하는 '실질 부하'는 (전체 부하 - 태양광 발전량) 입니다.
    # 즉, 태양광이 꺼지면 VSG가 그만큼 더 짊어져야 합니다.
    P_required_from_vsg_mech = config.P_load_total - P_solar

    # 3. VSG의 전기적 출력 (Swing Eq의 P_elec)
    # 현재 위상차(delta)에 의해 전력망으로 실제 흘러나가는 전력
    P_vsg_elec = (config.V_vsg * config.V_grid / config.X_line) * np.sin(delta)

    # 4. 미분 방정식 (Swing Equation)
    # 2H * d_omega_dt = P_mech_ref - P_elec - D*(omega - omega0)
    # 여기서 P_mech_ref는 VSG가 '내기로 약속한' 기준 출력이지만,
    # 하이브리드 제어에서는 수급 불균형(P_required - P_elec)이 관성 에너지로 충당됨을 표현

    # 입력(P_m): VSG의 기준 출력 (초기 상태 유지하려 함)
    # 외란: P_solar가 줄어들면, 전체 수급에서 구멍이 남.
    # 이 구멍을 시뮬레이션하기 위해 P_m을 고정하고 P_load 변화로 해석하는 것이 일반적임.

    # 초기 평형 상태(t=0)에서의 VSG 분담분
    P_vsg_ref = config.P_load_total - config.P_solar_initial

    d_delta_dt = omega - config.Omega_0

    # 가속/감속 토크 = (기계적 입력 - 전기적 출력)
    # 전기적 출력이 부하보다 작으면 가속, 크면 감속
    # 여기서는 "갑자기 태양광이 줄어서 VSG가 더 많은 전력을 내보내야 하는 상황"을 모사
    # P_solar가 줄어듦 -> Load가 VSG에게 더 많은 전력을 요구함 -> P_elec는 delta에 의해 결정됨
    # 수급 불균형 = P_vsg_ref - P_vsg_elec
    # *주의*: 태양광 감소는 '물리적 외란'이므로 Swing Equation의 입력항이 아니라
    # 시스템의 전력 균형점 이동으로 해석해야 함.

    # 간단한 모델링을 위해:
    # "태양광이 줄어든 만큼, 마치 부하가 늘어난 것과 동일한 충격을 받는다"
    current_load_imbalance = (config.P_load_total - P_solar) - P_vsg_elec

    d_omega_dt = (
        (1 / (2 * config.H))
        * (
            current_load_imbalance
            - config.D * (omega - config.Omega_0) / config.Omega_0
        )
        * config.Omega_0
    )

    return [d_delta_dt, d_omega_dt]
