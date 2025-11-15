def formatTimeInSeconds(time: float) -> str:
    if time < 0:
        time = 0
    minutes = int(time // 60)
    seconds = int(time % 60)
    return f"{minutes:02d}:{seconds:02d}"
