# config.py
import numpy as np


class Config:
    def __init__(self):
        # --- 시간 설정 ---
        self.t_start = 0.0
        self.t_end = 10.0
        self.steps = 1000

        # --- 전력망 파라미터 ---
        self.F_base = 60.0
        self.Omega_0 = 2 * np.pi * self.F_base
        self.X_line = 0.5

        # --- 이벤트: 전압 강하 (Voltage Sag) ---
        # 2초에 전력망 전압이 1.0 -> 0.95로 떨어짐 (사고 발생)
        self.V_grid_normal = 1.0
        self.V_grid_fault = 0.9
        self.event_time = 2.0

        # --- VSG 파라미터 (P-f) ---
        self.H = 5.0
        self.D = 10.0
        self.P_ref = 0.5  # 기준 유효 전력

        # --- VSG 파라미터 (Q-V) [신규 추가] ---
        self.V_ref_base = 1.0  # 기준 전압
        self.K_q = 0.5  # 무효전력 드룹 계수 (클수록 전압 유지 능력 강화)
        self.T_v = 0.1  # 전압 제어기 시상수 (응답 속도)
