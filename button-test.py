from gpiozero import Button
from gpiozero import LED

button = Button(3)

led = LED(15)

while True:
    if button.is_pressed:
        led.on()
        print("button is pressed")
    else:
        led.off()
