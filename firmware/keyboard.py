# this script's used to remote control the rover using keypresses
from Motor import *
from Servo import Servo


def keyboardLoop():
    # create the servo controller class
    servo = Servo()
    while True:
        key = input("Control the rover: ")
        key = key.lower()
        if key == "q":
            # left
            servo.moveToAngle("0", 150)
        elif key == "e":
            # right
            servo.moveToAngle("0", 30)
        elif key == "1":
            # up
            servo.moveToAngle("1", servo.upAngle + servo.turnSpeed)
        elif key == "2":
            # down
            servo.moveToAngle("1", servo.upAngle - servo.turnSpeed)
        elif key == "0":
            servo.moveToAngle("0", 0)


if __name__ == '__main__':
    keyboardLoop()