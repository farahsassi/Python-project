import RPi.GPIO as GPIO
import time
import picamera
import smtplib
from email import message

# configuration des ports
GPIO.setmode(GPIO.BCM)  # mode de numeration des GPIO
# initialisation des ports en E/S
# port du capteur piezo
GPIO.setup(2, GPIO.IN)
# port de camera
GPIO.setup(10, GPIO.OUT)
# port du servomotor
GPIO.setup(17, GPIO.OUT)
# Configuration du GPIO 18 du PWM
pwm_GPIO = 18
frequence = 50
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)


# Configuration de l'angle de servomotor


def angle_to_percent(angle):
    if angle > 180 or angle < 0:
        return False
    start = 2  # pourcentage de l'angle 0
    end = 12.5  # pourcentage de l'angle 180
    # methode de calcule de pourcentage des autres angles
    ratio = (end - start) / 180
    angle_as_percent = angle * ratio
    return start + angle_as_percent


# Init at 0°
pwm.start(angle_to_percent(0))
time.sleep(1)
# Go at 90° (the middle)
pwm.ChangeDutyCycle(angle_to_percent(90))
time.sleep(1)
# Finish at 180°
pwm.ChangeDutyCycle(angle_to_percent(180))
time.sleep(1)

# EN CAS DE DETECTION DE MOUVEMENT


GPIO.add_event_detect(2, GPIO.RISING)  # detection du front montant càd detection de mouvement
if GPIO.event_detected(2):
    print("detection de mouvement")
    # activation de la camera
    camera = picamera.PiCamera()
    camera.start_preview()
    # rotation du servomotor
    for angle in range(0, 180):
        pwm.ChandeDutyCycle(angle_to_percent(angle))
        # capture de l'image
        image = camera.capture()
        camera.stop_preview()
    # envoie de l'email au proprietaire
    from_addr = 'home@gmail.com'
    to_addr = 'owner@gmail.com'
    subject = 'MOVEMENT DETECTED!!!'
    content = image
    msg = message.Message()
    msg.add_header('from', from_addr)
    msg.add_header('to', to_addr)
    msg.add_header('subject', subject)
    msg.add_header('content', image)
    server = smtplib.SMTP('smtp.gmail.com')
    server.login(from_addr, 'homesecurity')
    server.send_message(msg, from_addr=from_addr, to_addrs=[to_addr])

pwm.stop()
GPIO.cleanup()