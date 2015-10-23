#!/bin/env python2
import pifacecad
import sys, time, os, re
import OSC

modes = ["bpm","choose","nudge","bars","loop"]
mode = modes[1]
bpm = 132.0
original_bpm = 132.0
rate = bpm/original_bpm

# CAD
cad = pifacecad.PiFaceCAD()
lcd = cad.lcd
lcd.clear()
lcd.backlight_on()

# OSC
osc_client = OSC.OSCClient()
osc_client.connect(('127.0.0.1', 6449))   # localhost, port 57120

# files
root_dir = "/mnt/usb/stems"
files = os.listdir(root_dir)
file_idx = 0
current = ""

def osc_send(addr,param):
  osc_msg = OSC.OSCMessage()
  osc_msg.setAddress(addr)
  if type(param) is list:
    for p in param:
      osc_msg.append(p)
  else:
    osc_msg.append(param)
  print(osc_msg)
  osc_client.send(osc_msg)

def choose(i):
  global file_idx
  file_idx = file_idx + i
  if file_idx < 0: file_idx = len(files)-1
  elif file_idx >= len(files): file_idx = 0

def stems():
  d = root_dir+"/"+current
  return [os.path.join(d, f) for f in os.listdir(d)]

def load():
  global current, original_bpm
  if current != files[file_idx]:
    current = files[file_idx]
    original_bpm = float(re.match('^\d\d\d',current).group())
    osc_send("/load",stems())
    set_bpm(bpm)

def set_bpm(new_bpm):
  global bpm, rate
  bpm = new_bpm
  rate = bpm/original_bpm
  osc_send("/rate",rate)

def move(samples):
  osc_send("/position",int(samples))

def move_bars(bars):
  move(bars*bar())

def move_beats(beats):
  move(beats*beat())

def move_ms(ms):
  move(ratio*ms*44100/1000)

def bar(): # nr of samples in 1 bar 
  return 4*44100*60/original_bpm

def beat(): # nr of samples in 1 bar 
  return 44100*60/original_bpm

def loop(bars):
  loop_size = bars*bar()
  loop_nr = current_pos() // loop_size # floor division
  start = loop_nr*loop_size
  osc_send("/loop",start,loop_size)

def noloop():
  osc_send("/loop",0,0)

def update_display():
  lcd.clear()
  lcd.blink_off()
  string = str(int(round(bpm))) + " " + files[file_idx]
  lcd.write(string)
  if mode == modes[0]:
    lcd.set_cursor(2,0)
  elif mode == modes[1]:
    lcd.set_cursor(4,0)
    if files[file_idx] != current: lcd.blink_on()

def select_mode(event):
  global mode
  mode = modes[event.pin_num]
  if event.pin_num == 4: quit()
  update_display()

def quit():
  # TODO kill chuck?
  listener.deactivate()
  sys.exit()
  # poweroff


def edit(event):
  if mode == modes[0]:
    if event.pin_num == 6: set_bpm(bpm-1)
    elif event.pin_num == 7: set_bpm(bpm+1)
  elif mode == modes[1]:
    if event.pin_num == 5: load()
    elif event.pin_num == 6: choose(-1)
    elif event.pin_num == 7: choose(1)
  elif mode == modes[3]:
    if event.pin_num == 6: move_bars(-8)
    elif event.pin_num == 7: move_bars(8)
  update_display()
    
listener = pifacecad.SwitchEventListener(chip=cad)
for i in range(5):
    listener.register(i, pifacecad.IODIR_ON, select_mode)

for i in range(5,8):
    listener.register(i, pifacecad.IODIR_ON, edit)

update_display()
listener.activate()
#time.sleep(15)
