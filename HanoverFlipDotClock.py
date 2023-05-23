from datetime import datetime
from HanoverDisplay import HanoverDisplay

display=HanoverDisplay("COM4")

while True:
    now_time=datetime.now()

    big_display_time = now_time.strftime("%I:%M").lstrip("0")
    big_display_length = len(big_display_time)
    if now_time.second > 56 or now_time.second < 4:
        small_display_seconds = now_time.strftime("%S")
    else:
        small_display_seconds =""
        if now_time.hour >=12:
            small_display_seconds = small_display_seconds + "pm"
        else:
            small_display_seconds = small_display_seconds + "am"
    display.clear()
    display.set_big_font()
    display.set_message(big_display_time)
    display.set_small_font()
    display.set_message(small_display_seconds)

    display.update_hanover()
    
