# models/stability_analyzer.py
import numpy as np
import matplotlib.pyplot as plt


def plot_stability_region(config):
    """
    전력망 임피던스(X)와 전력(P) 사이의 안정도 영역(Stability Region)을 시각화합니다.
    이론적 최대 전력 전송 한계(Static Stability Limit)를 계산하여 그립니다.
    """
    print("--- Generating Stability Region Map ---")

    # 1. X축: 전력망 임피던스 범위 설정 (0.1 ~ 1.5 p.u.)
    # 0.1(강한 전력망) -> 1.5(매우 약한 전력망)
    x_range = np.linspace(0.1, 1.5, 200)

    # 2. 이론적 최대 전력 곡선 계산 (P_max = V*V / X)
    # V_vsg와 V_grid는 1.0 p.u.로 가정
    v_vsg = 1.0
    v_grid = 1.0
    p_max_curve = (v_vsg * v_grid) / x_range

    # 3. 그래프 그리기
    plt.figure(figsize=(10, 8))

    # (1) 경계선 그리기
    plt.plot(
        x_range,
        p_max_curve,
        "r-",
        linewidth=3,
        label="Static Stability Limit (Theoretical)",
    )

    # (2) 영역 채우기 (Fill Between)
    # 곡선 아래: 안정 영역 (Stable)
    plt.fill_between(
        x_range, 0, p_max_curve, color="blue", alpha=0.1, label="Stable Region"
    )
    # 곡선 위: 불안정 영역 (Unstable) - 그래프 상단까지
    plt.fill_between(
        x_range, p_max_curve, 3.0, color="red", alpha=0.1, label="Unstable Region"
    )

    # (3) 현재 시뮬레이션 설정 포인트 표시
    current_x = config.X_line
    current_p = config.P_ref

    # 현재 포인트가 안정/불안정 어디에 있는지 판별
    limit_at_current_x = (v_vsg * v_grid) / current_x
    status = "Stable" if current_p < limit_at_current_x else "Unstable"
    marker_color = "blue" if status == "Stable" else "red"

    plt.scatter(
        [current_x],
        [current_p],
        color=marker_color,
        s=200,
        edgecolors="k",
        zorder=10,
        label=f"Current Operation\n(X={current_x}, P={current_p})",
    )

    # (4) 화살표 및 텍스트 주석 (그래프 설명)
    plt.annotate(
        f"Current Status: {status}",
        xy=(current_x, current_p),
        xytext=(current_x + 0.1, current_p + 0.5),
        arrowprops=dict(facecolor="black", shrink=0.05),
        fontsize=12,
        fontweight="bold",
    )

    # 그래프 스타일 설정
    plt.xlim(0.1, 1.5)
    plt.ylim(0, 2.5)
    plt.xlabel("Grid Impedance $X_{line}$ [p.u.] (Weakness)", fontsize=14)
    plt.ylabel("Active Power Output $P$ [p.u.]", fontsize=14)
    plt.title("P-X Stability Region Map (Weak Grid Constraints)", fontsize=16)
    plt.grid(True, which="both", linestyle="--")
    plt.legend(loc="upper right", fontsize=12)

    plt.tight_layout()
    plt.show()
    print("--- Map Generated ---")
