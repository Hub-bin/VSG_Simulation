# config.py
import numpy as np


class Config:
    def __init__(self):
        # --- 시뮬레이션 시간 설정 ---
        self.t_start = 0.0
        self.t_end = 20.0  # 관찰 시간을 좀 더 길게 (20초)
        self.steps = 2000

        # --- 전력망(Grid) 파라미터 ---
        self.F_base = 60.0
        self.Omega_0 = 2 * np.pi * self.F_base
        self.V_grid = 1.0
        self.X_line = 0.5

        # --- VSG (배터리) 파라미터 ---
        self.V_vsg = 1.0
        self.H = 5.0  # VSG 관성 (이 값을 줄여서 테스트해보면 차이가 큼)
        self.D = 10.0

        # --- 시나리오: 태양광 급감 (Cloud Passing Effect) ---
        self.P_load_total = 0.8  # 전체 부하량 (p.u.)
        self.P_solar_initial = 0.5  # 초기 태양광 발전량 (p.u.)
        self.P_solar_drop = 0.3  # 태양광 발전 감소량 (0.5 -> 0.2로 뚝 떨어짐)
        self.event_time = 5.0  # 5초에 구름이 지나감
