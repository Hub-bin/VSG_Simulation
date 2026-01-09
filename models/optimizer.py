# models/optimizer.py
import numpy as np
from scipy.integrate import odeint
from models.hybrid_system import system_dynamics


def find_optimal_inertia(config, safety_threshold=59.2):
    """
    이진 탐색(Binary Search)을 사용하여
    주파수 최저점(Nadir)이 safety_threshold를 지키는
    '최소한의 관성 상수(H)'를 찾습니다.
    """

    # 탐색 범위 설정 (H값)
    h_min = 0.1  # 최소 범위
    h_max = 20.0  # 최대 범위
    tolerance = 0.05  # 허용 오차 (이 정도 정밀도면 멈춤)

    optimal_h = None
    iteration = 0

    print(f"--- Optimization Started (Target Nadir >= {safety_threshold} Hz) ---")

    while (h_max - h_min) > tolerance:
        iteration += 1

        # 1. 중간값 선택
        h_mid = (h_min + h_max) / 2

        # 2. 시뮬레이션 수행 (임시 H값 적용)
        original_h = config.H
        config.H = h_mid

        # 초기 상태 계산 (H는 동역학에만 영향, 초기 평형점은 H와 무관하지만 코드 구조상 수행)
        P_vsg_initial = config.P_load_total - config.P_solar_initial
        P_max = config.V_vsg * config.V_grid / config.X_line
        delta_0 = np.arcsin(P_vsg_initial / P_max)
        y0 = [delta_0, config.Omega_0]

        t = np.linspace(config.t_start, config.t_end, config.steps)
        sol = odeint(system_dynamics, y0, t, args=(config,))

        # 설정 복구
        config.H = original_h

        # 3. 결과 분석 (최저 주파수 확인)
        freq_res = sol[:, 1] / (2 * np.pi)
        nadir = np.min(freq_res)

        # 4. 판단 및 범위 좁히기
        if nadir < safety_threshold:
            # 주파수가 너무 많이 떨어짐 -> 관성(H)이 더 필요함 -> 범위의 아랫부분을 버림
            print(
                f"Iter {iteration}: H={h_mid:.2f} -> Nadir {nadir:.4f} Hz (FAIL - Too Low)"
            )
            h_min = h_mid
        else:
            # 주파수가 안전함 -> 관성(H)을 줄여서 비용을 아낄 수 있는지 확인 -> 범위의 윗부분을 버림
            print(
                f"Iter {iteration}: H={h_mid:.2f} -> Nadir {nadir:.4f} Hz (PASS - Safe)"
            )
            optimal_h = h_mid  # 일단 저장
            h_max = h_mid

    print(f"--- Optimization Finished. Optimal H = {optimal_h:.2f} ---")
    return optimal_h
