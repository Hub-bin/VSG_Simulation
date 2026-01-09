# main.py
import numpy as np
from config import Config

# 새로 만든 모듈 import
from models.stability_analyzer import plot_stability_region


def main():
    print("=== VSG Simulation Step 7: Stability Region Analysis ===")

    # 설정 로드
    cfg = Config()

    # [사용자 설정 테스트]
    # 여기서 값을 바꿔보며 그래프 상의 위치 변화를 확인하세요.
    # Case 1: 안정적인 상황 (기본값) -> X=0.5, P=0.5
    cfg.X_line = 0.5
    cfg.P_ref = 0.5

    # Case 2: 매우 약한 전력망에서 무리하게 전력을 보내는 상황 (테스트용)
    # 아래 주석을 풀고 실행해보세요. 점이 빨간색 영역(불안정)으로 넘어갑니다.
    # cfg.X_line = 1.2  # 아주 약한 전력망
    # cfg.P_ref = 1.0   # 높은 전력 전송 시도

    # 안정도 지도 그리기
    plot_stability_region(cfg)

    print("=== Analysis Finished ===")


if __name__ == "__main__":
    main()
