# main.py
import numpy as np
from scipy.integrate import odeint
from config import Config
from models.avm_system import voltage_dynamics  # 변경됨
from utils.visualizer import plot_voltage_control  # 변경됨


def main():
    print("=== VSG Simulation Step 6: Voltage Control (AVR & Q-V Droop) ===")
    cfg = Config()

    # 1. 초기 상태 설정
    # V_vsg 초기값은 1.0이라고 가정
    # P = V*V/X * sin(delta) -> delta 역산 (V=1.0 가정)
    P_max = 1.0 * 1.0 / cfg.X_line
    delta_0 = np.arcsin(cfg.P_ref / P_max)

    # 초기 상태 벡터: [delta, omega, V_vsg]
    y0 = [delta_0, cfg.Omega_0, 1.0]

    # 2. 시뮬레이션
    t = np.linspace(cfg.t_start, cfg.t_end, cfg.steps)
    sol = odeint(voltage_dynamics, y0, t, args=(cfg,))

    # 3. 결과 시각화
    plot_voltage_control(t, sol, cfg)
    print("=== Simulation Finished ===")


if __name__ == "__main__":
    main()
