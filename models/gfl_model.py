# models/gfl_model.py


def get_solar_power(t, config):
    """
    시간 t에 따른 태양광(GFL) 출력 전력을 반환
    5초(event_time)에 출력이 급격히 감소(Step Drop)하는 시나리오
    """
    if t >= config.event_time:
        # 구름이 끼어 발전량이 뚝 떨어짐
        return config.P_solar_initial - config.P_solar_drop
    else:
        # 정상 발전 중
        return config.P_solar_initial
