# models/eigen_analysis.py
import numpy as np
import matplotlib.pyplot as plt


def get_linearized_matrix(config, x_line_val):
    """
    주어진 조건에서 시스템을 선형화하여 상태 행렬 A를 반환
    상태 변수: [delta, omega]
    """
    # 1. 평형점(Operating Point) 계산
    # V_vsg와 V_grid가 config에 존재하는지 확인 (없으면 기본값 1.0 사용)
    v_vsg = getattr(config, "V_vsg", 1.0)
    v_grid = getattr(config, "V_grid", 1.0)

    P_max = (v_vsg * v_grid) / x_line_val

    if config.P_ref > P_max:
        return None  # 불안정 (해 없음)

    delta_0 = np.arcsin(config.P_ref / P_max)

    # 2. 선형화 계수 (Jacobian 요소)
    # 동기화 토크 계수 K_s = dP/d_delta
    K_s = (v_vsg * v_grid / x_line_val) * np.cos(delta_0)

    # 3. 상태 행렬 A 구성
    # d_delta = 0*delta + 1*omega
    # d_omega = (-K_s/2H)*delta - (D/2H)*omega

    A = np.array([[0, 1], [-K_s / (2 * config.H), -config.D / (2 * config.H)]])

    return A


def plot_root_locus(config):
    print("--- Generating Root Locus Plot ---")

    # 임피던스(X)를 0.2(강함)에서 1.2(약함)까지 변화시킴
    x_values = np.linspace(0.2, 1.2, 50)

    plt.figure(figsize=(10, 8))

    for x in x_values:
        A = get_linearized_matrix(config, x)
        if A is not None:
            eigs = np.linalg.eigvals(A)

            # [수정된 부분]
            # 고유값 개수만큼 색상 값(x)을 리스트로 복제하여 개수를 맞춤
            # vmin, vmax를 설정하여 루프 전체에서 색상 스케일 통일
            colors = [x] * len(eigs)

            plt.scatter(
                eigs.real,
                eigs.imag,
                c=colors,
                cmap="viridis",
                vmin=x_values.min(),
                vmax=x_values.max(),
                s=30,
                alpha=0.8,
            )

    # 허수축(안정도 경계) 표시
    plt.axvline(x=0, color="k", linestyle="--", label="Stability Boundary")

    # 그래프 꾸미기
    plt.colorbar(label="Grid Impedance ($X_{line}$)")
    plt.title("Root Locus Analysis (Effect of Weak Grid)", fontsize=16)
    plt.xlabel("Real Axis ($\sigma$)", fontsize=14)
    plt.ylabel("Imaginary Axis ($j\omega$)", fontsize=14)
    plt.grid(True)
    plt.xlim(-2, 0.5)  # 불안정 영역(오른쪽)을 보여주기 위해 범위 설정

    # 화살표 주석
    plt.annotate(
        "System becomes less stable\nas X increases",
        xy=(-0.1, 1.0),
        xytext=(-1.5, 2.0),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    print("--- Root Locus Generated ---")
    plt.show()
