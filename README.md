# evdev-joystick-calibration
Run, pick up the gamepad and turn sticks with triggers around. 

Note that this script was originally developed by 
Dima Kompot, <virusmater@gmail.com> and forked from that repository by
Nick Lawson, <70027408+nick-l-o3de@users.noreply.github.com> when the original author
closed their original repo and pointed everyone at the fork.  

Nick_L: "I guess I inherited this via the rule of you touch it you maintain it"

```bash
evdev-joystick-calibration -h
usage: evdev-joystick-calibration [-h] [-l] [-c]

Pick up the gamepad and turn sticks with triggers around.  Includes deadzone calibration.

optional arguments:
  -h, --help       show this help message and exit
  -l, --load       load configuration
  -c, --calibrate  calibrate and save configuration
```
# install
```bash
vektuz@pc:~$ sudo apt install python3-pip git -y
vektuz@pc:~$ sudo pip3 install git+https://github.com/nick-l-o3de/evdev-joystick-calibration
```

Alternatively, if you don't want to install it you can clone the repo, and run it as a module, ie
```bash
vektuz@pc:~$ git clone https://github.com/nick-l-o3de/evdev-joystick-calibration.git
vektuz@pc:~$ cd evdev-joystick-calibration
vektuz@pc:~$ python -m evdev-joystick-calibration
```


# example
## calibrate
```bash
vektuz@pc:~$ evdev-joystick-calibration
Available devices:
0 Microsoft X-Box 360 pad
Pick one device for the calibration: 0
Move sticks and triggers of Microsoft X-Box 360 pad to max and min positions. 
Press any button for next step.
analog: ABS_X min:-32768 max:32767 flat:0
Dead zone calibration (press a button to skip)
For each stick, quickly flick that stick to a diagonal (NE, NW, SE, or SW) and release it and let it recenter
Wait a moment, and then repeat this with a different stick and different diagonal.
Make sure to leave it alone for a moment after each release.
Do this until no more new dead zones or expansions are reported, then press any button.
ABS_RY  =  -1620         Initial Deadzone for  ABS_RX  is  1401.5
Initial Deadzone for  ABS_RY  is  1619.5
ABS_RX  =  -2960         Expanding deadzone for  ABS_RX  to  2959.5
ABS_RX  =  -363         Initial Deadzone for  ABS_Y  is  582.5
ABS_RY  =  -57         Initial Deadzone for  ABS_X  is  2359.5
ABS_X  =  1701         Expanding deadzone for  ABS_Y  to  2805.5
ABS_RX  =  -3271         Expanding deadzone for  ABS_RX  to  3270.5
ABS_RX  =  -1713         Expanding deadzone for  ABS_RY  to  2289.5
ABS_RY  =  -3295         Expanding deadzone for  ABS_RY  to  3294.5
ABS_Y  =  -3442         Initial Deadzone for  ABS_HAT0X  is  0.0
Initial Deadzone for  ABS_HAT0Y  is  0.0
Expanding deadzone for  ABS_Y  to  3441.5
ABS_RY  =  -839         Expanding deadzone for  ABS_Y  to  3547.5
Configuration for Microsoft X-Box 360 pad
analog: ABS_X min:-32768 max:32767 flat:2418
analog: ABS_RX min:-32768 max:32767 flat:3352
analog: ABS_Y min:-32768 max:32767 flat:3636
analog: ABS_RY min:-32768 max:32767 flat:3376
analog: ABS_RZ min:0 max:255 flat:0
analog: ABS_Z min:0 max:255 flat:0
analog: ABS_HAT0X min:-1 max:1 flat:0
analog: ABS_HAT0Y min:-1 max:1 flat:0
Configuration for Microsoft X-Box 360 pad saved at /home/vektuz/.config/evdev-joystick-calibration/MicrosoftX-Box360pad.json
```
## load
```bash
vektuz@pc:~$ evdev-joystick-calibration -l
Configuration for Microsoft X-Box 360 pad loaded from /home/vektuz/.config/evdev-joystick-calibration/MicrosoftX-Box360pad.json
Configuration for Microsoft X-Box 360 pad
analog: ABS_X min:-32768 max:32767 flat:2418
analog: ABS_RX min:-32768 max:32767 flat:3352
analog: ABS_Y min:-32768 max:32767 flat:3636
analog: ABS_RY min:-32768 max:32767 flat:3376
analog: ABS_RZ min:0 max:255 flat:0
analog: ABS_Z min:0 max:255 flat:0
analog: ABS_HAT0X min:-1 max:1 flat:0
analog: ABS_HAT0Y min:-1 max:1 flat:0
```
# requirements
https://github.com/gvalkov/python-evdev

The user should be able to write to the evdev device. Example of udev rule for Nintendo Wii Remote Classic Controller
```bash
kompot@pc:~$ sudo nano /etc/udev/rules.d/99-wiimote.rules 
SUBSYSTEM=="input", ATTRS{name}=="Nintendo Wii Remote Classic Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1", ENV{ID_INPUT_KEY}="0"
```
# auto load configuration on connect
1. Run calibration **as root** (unfortunatelly all udev rules are executed under root and there is no way to get current user. if you know how to avoid it - please let me know):
```bash
kompot@pc:~$ sudo evdev-joystick-calibration -c
```
2. Make new udev rule for add action:
```bash
kompot@pc:~$ sudo nano /etc/udev/rules.d/99-wiimote.rules 
SUBSYSTEM=="input", ATTRS{name}=="Nintendo Wii Remote Classic Controller", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1", ENV{ID_INPUT_KEY}="0"
SUBSYSTEM=="input", KERNEL=="event*", ACTION=="add", ATTRS{name}=="Nintendo Wii Remote Classic Controller", RUN+="/bin/sh -c 'evdev-joystick-calibration -l'"
```
3. Reload rules:
```bash
sudo udevadm control --reload-rules
```
