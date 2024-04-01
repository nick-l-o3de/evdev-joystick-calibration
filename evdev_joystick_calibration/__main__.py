import argparse
import time
import sys

import evdev
from evdev import ecodes

from evdev_joystick_calibration import configuration
from evdev_joystick_calibration.MinMaxItem import MinMaxItem


def main():
    parser = argparse.ArgumentParser(description='Pick up the gamepad and turn sticks with triggers around')
    parser.add_argument('-l', '--load', action='store_true', help='load configuration')
    parser.add_argument('-c', '--calibrate', action='store_true', help='calibrate and save configuration')
    args = parser.parse_args()
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    # If only load configuration - load available and exit
    if args.load:
        for index, device in enumerate(devices):
            if ecodes.EV_ABS in device.capabilities():
                try:
                    configuration.apply(device, configuration.load(device.name))
                except FileNotFoundError:
                    print("Skip", device.name)
                finally:
                    device.close()
        exit()

    # get all devices with analogs
    print('Available devices:')
    for index, device in enumerate(devices):
        if ecodes.EV_ABS in device.capabilities():
            print(index, device.name)
    print('Pick one device for the calibration:', end=" ")
    try:
        index = int(input())
    except: # if not a number
        print("Invalid entry")
        return
    
    print('Move sticks and triggers of', devices[index].name, 'to max and min positions. ')
    print('Press any button for next step.')
    
    min_max = {}
    device = devices[index]
    try:
        for event in device.read_loop():
            # exit if a regular key was pressed
            if event.type == ecodes.EV_KEY:
                if event.value == 0: # respond only to key release
                    # one issue here is that some controllers consider trigger pulls to be button presses
                    # as well as axis movements.  Consider ignoring events that are also axis pulls...
                    if event.code in [ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_TL2, ecodes.BTN_TR2]:
                        continue # ignore trigger presses
                    break
            if event.type == ecodes.EV_ABS:
                if event.code not in min_max:
                    analog_name = str(evdev.categorize(event)).partition(", ")[2]
                    min_max[event.code] = MinMaxItem(analog_name, event.value, event.value, 0)
                if min_max[event.code].minimum > event.value:
                    min_max[event.code].minimum = event.value
                if min_max[event.code].maximum < event.value:
                    min_max[event.code].maximum = event.value

                analog_name = ecodes.ABS[event.code]
                print("\r" + str(min_max[event.code]), "       ", end=" ")

        # drain all remaining events
        while device.read_one():
            pass

        # we're going to ask the user to move the sticks and then release them one by one.
        # we'll then look at the maximum distance from the center that the stick reached after some delay.
        # we'll then use that as the deadzone for that stick.

        # there are some problems with this
        # problem 1 (unsolved) - triggers don't ever center, they count as released when they are at 0 and often have range 0-N
        #                        to fix this, we'd have to collect resting state data first, and consider that to be the center.

        print('Dead zone calibration (press a button to skip)')
        print('For each stick, quickly flick that stick to a diagonal (NE, NW, SE, or SW) and release it and let it recenter')
        print('Wait a moment, and then repeat this with a different stick and different diagonal.')
        print('Make sure to leave it alone for a moment after each release.')
        print('Do this until no more new dead zones or expansions are reported, then press any button.')

        last_timestamp = {}
        last_value = {}
        current_deadzones = {}
        last_event = time.time()

        while True:
            epoch_time = time.time()
            event = device.read_one()
            if event is not None:
                if event.type == ecodes.EV_KEY:
                    if event.code in [ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_TL2, ecodes.BTN_TR2]:
                        continue # ignore trigger presses
                    break
                if event.type == ecodes.EV_ABS:
                    if event.code in min_max:
                        if event.code in last_value:
                            # some axes do not jitter at all and some jitter all the time.
                            # only consider devices that have an actual range of values here to be jitterable.
                            if abs(last_value[event.code] - event.value) < 2 and min_max[event.code].maximum > 1:
                                last_value[event.code] = event.value
                                continue # don't consider this as actually having been moved at all
                        last_value[event.code] = event.value
                        last_timestamp[event.code] = epoch_time
                        last_event = epoch_time
                        print("\r" + str(min_max[event.code].analog), " = ", event.value, "       ", end=" ")
            
            if epoch_time - last_event < 0.5:
                continue # don't bother doing much until time has passed
            
            for key in min_max.keys():
                if key in last_timestamp:
                    if epoch_time - last_timestamp[key] > 0.5:
                        absinfo = device.absinfo(key)
                        centerpt = (min_max[key].minimum + min_max[key].maximum) / 2
                        # we are here assuming that no device has stick drift worse than 20% of its actual range of motion
                        deadZoneThreshhold = (min_max[key].maximum - min_max[key].minimum) * 0.20
                        distanceFromCenter = abs(absinfo.value - centerpt)
                        if distanceFromCenter < deadZoneThreshhold:
                            if key not in current_deadzones:
                                print("Initial Deadzone for ", min_max[key].analog, " is ", distanceFromCenter)
                                current_deadzones[key] = distanceFromCenter
                            else:
                                if distanceFromCenter > current_deadzones[key]:
                                    print("Expanding deadzone for ", min_max[key].analog, " to ", distanceFromCenter)
                                    current_deadzones[key] = distanceFromCenter
                            # once we pick a deadzone, we don't look at it again until that axis starts moving again.
                            del last_timestamp[key]

        for key in current_deadzones.keys():
            # expand the dead zones slightly, just to be safe, by say 2.5%
            min_max[key].flat = int(current_deadzones[key] * 1.025)

    except KeyboardInterrupt:
        print('\rSave and apply the configuration? (y/n)', end=" ")
        answer = str(input())
        if answer == "y":
            pass
        else:
            exit()

    configuration.apply(device, min_max)
    configuration.store(device.name, min_max)
    device.close()

if __name__ == '__main__':
    main()
