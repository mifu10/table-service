import time
import logging
import json
import random
import threading

from enum import Enum
from agt import AlexaGadget

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, SpeedPercent, MediumMotor, LargeMotor

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO)


class Direction(Enum):
    """
    The list of directional commands and their variations.
    These variations correspond to the skill slot values.
    """
    FORWARD = ['forward', 'forwards', 'go forward']
    BACKWARD = ['back', 'backward', 'backwards', 'go backward']
    LEFT = ['left', 'go left']
    RIGHT = ['right', 'go right']
    STOP = ['stop', 'brake']


class MindstormsGadget(AlexaGadget):
    """
    A Mindstorms gadget that performs movement based on voice commands.
    Two types of commands are supported, directional movement and preset.
    """

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Gadget state
        self.patrol_mode = False

        # Ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.drive = MoveTank(OUTPUT_A,OUTPUT_A)  # Band """
        self.deliver = MoveTank(OUTPUT_B,OUTPUT_B) # Deliver """

        # Start threads
        #threading.Thread(target=self._patrol_thread, daemon=True).start()

    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        self.leds.set_color("LEFT", "GREEN")
        self.leds.set_color("RIGHT", "GREEN")
        print("{} connected to Echo device".format(self.friendly_name))

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        self.leds.set_color("LEFT", "BLACK")
        self.leds.set_color("RIGHT", "BLACK")
        print("{} disconnected from Echo device".format(self.friendly_name))

    def on_custom_mindstorms_gadget_control(self, directive):
        """
        Handles the Custom.Mindstorms.Gadget control directive.
        :param directive: the custom directive with the matching namespace and name
        """
        try:
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Control payload: {}".format(payload))
            control_type = payload["type"]
            if control_type == "move":
                # Expected params: [direction, duration, speed]
                self._move(payload["direction"], int(payload["duration"]), int(payload["speed"]))
            if control_type == "deliver":
                # Expected params: [direction, duration, speed]
                self._deliver(payload["direction"], int(payload["duration"]), int(payload["speed"]),payload["spice"])
        
        except KeyError:
            print("Missing expected parameters: {}".format(directive))

    def _move(self, direction, duration, speed, is_blocking=False):
        """
        Handles move commands from the directive.
        Right and left movement can under or over turn depending on the surface type.
        :param direction: the move direction
        :param duration: the duration in seconds
        :param speed: the speed percentage as an integer
        :param is_blocking: if set, motor run until duration expired before accepting another command
        """
        print("Move command: ({}, {}, {}, {})".format(direction, speed, duration, is_blocking))
        if direction in Direction.FORWARD.value:
            self.drive.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), duration, block=is_blocking)
           # self.drive.run_timed(speed_sp=speed, time_sp=duration)  
           # self.drive.run_timed(speed_sp=750, time_sp=2500)
        if direction in Direction.BACKWARD.value:
           self.drive.on_for_seconds(SpeedPercent(-speed), SpeedPercent(-speed), duration, block=is_blocking)
           # self.drive.run_timed(speed_sp=-speed, time_sp=duration)  
  
        if direction in Direction.STOP.value:
            self.drive.off()
            self.patrol_mode = False

    def _deliver(self, direction, duration, speed, spice, is_blocking=False):

        #print("Move command: ({}, {}, {}, {})".format(direction, speed, duration, is_blocking))

        # Define the speed and duration for band and deliver motor depending on the spice
        if (spice == 'salt'):
            SpeedBand = 16
            Durationband = 2
            SpeedDeliver = 15
            DurationDeliver = 3

        if (spice == 'pepper'):
            SpeedBand = 0
            Durationband = 0
            SpeedDeliver = 15
            DurationDeliver = 3

        if spice == 'lemon':
            SpeedBand = -16
            Durationband = 2
            SpeedDeliver = 15
            DurationDeliver = 3


        if spice != '':
            self.leds.set_color("LEFT", "ORANGE")
            self.leds.set_color("RIGHT", "ORANGE")

            #Band position to correct spice
            self.drive.on_for_seconds(SpeedPercent(-SpeedBand), SpeedPercent(-SpeedBand), Durationband, block=is_blocking)   
            time.sleep(4)

            # deliver spice
            self.deliver.on_for_seconds(SpeedPercent(SpeedDeliver), SpeedPercent(SpeedDeliver), DurationDeliver, block=is_blocking)
            time.sleep(4)

            # # deliver motor to init
            self.deliver.on_for_seconds(SpeedPercent(-SpeedDeliver), SpeedPercent(-SpeedDeliver), DurationDeliver, block=is_blocking)
            time.sleep(4)

            #Band back to init
            self.drive.on_for_seconds(SpeedPercent(SpeedBand), SpeedPercent(SpeedBand), Durationband, block=is_blocking)  
            time.sleep(4)

            # make some noise and blinking after the delivery 
            self.sound.play_song((('E5', 'q'), ('E5', 'q')))
            self.sound.speak('Enjoy your meal')

            self.leds.set_color("LEFT", "GREEN")
            self.leds.set_color("RIGHT", "GREEN")

    

if __name__ == '__main__':

    # Startup sequence
    gadget = MindstormsGadget()
    gadget.sound.play_song((('C4', 'e'), ('D4', 'e'), ('E5', 'q')))
    gadget.leds.set_color("LEFT", "GREEN")
    gadget.leds.set_color("RIGHT", "GREEN")

    # Gadget main entry point
    gadget.main()

    # Shutdown sequence
    gadget.sound.play_song((('E5', 'e'), ('C4', 'e')))
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")
