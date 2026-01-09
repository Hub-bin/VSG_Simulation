# config.py (기존 내용 유지하되, 아래 내용 추가/수정)
import numpy as np


class Config:
    def __init__(self):
        # ... (기존 설정들: t_start, Grid, VSG 등등) ...
        self.t_start = 0.0
        self.t_end = 10.0
        self.steps = 1000

        self.F_base = 60.0
        self.Omega_0 = 2 * np.pi * self.F_base

        # [테스트 조건] 매우 약한 전력망 (X=1.2)
        # 일반 제어로는 불안정한 조건입니다.
        self.V_grid = 1.0
        self.X_line = 1.2  # High Impedance (Weak Grid)
        self.V_vsg = 1.0

        self.H = 3.0  # 관성도 낮춤 (불안정 유발)
        self.D = 5.0
        self.P_ref = 0.8  # 높은 부하

        # ... (태양광 설정 등은 생략 가능) ...
        self.P_load_total = 0.8
        self.P_solar_initial = 0.0  # Solar 없이 테스트
        self.P_solar_drop = 0.0

        self.V_grid_normal = 1.0
        self.V_grid_fault = 1.0  # 전압 사고 없음 (자체 진동 관찰)
        self.event_time = 1.0  # 1초에 부하 투입한다고 가정

        self.V_ref_base = 1.0
        self.K_q = 0.5
        self.T_v = 0.1

        # --- [Step 11 신규 추가] 제안 기법 파라미터 ---
        self.use_proposed_control = False  # True면 논문 기법 적용
        self.K_nvr = 0.05  # 음의 가상 저항 게인 (Damping Gain)
