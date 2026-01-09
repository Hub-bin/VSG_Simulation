# config.py
import numpy as np


class Config:
    def __init__(self):
        # --- [1] 시뮬레이션 공통 설정 ---
        self.t_start = 0.0
        self.t_end = 20.0  # 충분한 시간 관측
        self.steps = 2000  # 해상도

        # --- [2] 전력망(Grid) 파라미터 ---
        self.F_base = 60.0
        self.Omega_0 = 2 * np.pi * self.F_base

        # 분석(Analysis)용 기준 전압 (Step 7, 8, 9에서 사용)
        self.V_grid = 1.0
        self.X_line = 0.5

        # --- [3] VSG (배터리) 파라미터 ---
        # 분석(Analysis)용 기준 전압 (에러 발생했던 부분)
        self.V_vsg = 1.0

        self.H = 5.0  # 관성 상수
        self.D = 10.0  # 감쇠 계수
        self.P_ref = 0.5  # 기준 출력

        # --- [4] 태양광 및 부하 시나리오 (Step 3, 4, 5) ---
        self.P_load_total = 0.8
        self.P_solar_initial = 0.5
        self.P_solar_drop = 0.3

        # --- [5] 전압 제어(AVR) 및 사고 시나리오 (Step 6) ---
        self.V_grid_normal = 1.0  # 정상 시 전력망 전압
        self.V_grid_fault = 0.9  # 사고 시 전력망 전압
        self.V_ref_base = 1.0  # 배터리 목표 전압
        self.K_q = 0.5  # 무효전력 드룹 계수
        self.T_v = 0.1  # 전압 제어기 시상수

        # 이벤트 발생 시간 (공통)
        self.event_time = 2.0
