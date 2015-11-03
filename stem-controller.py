#!/bin/env python2
'''
TODO
  time display update
  bpm preselect
  nudge
  skip 16th,8th,4th
'''

import pifacecad
import sys, time, os, re, thread
import OSC

# global variables
modes = ["select","bpm","nudge","bars","cue"]
mode = modes[0]
bpm = 132.0
new_bpm = 132.0
original_bpm = 132.0
rate = bpm/original_bpm
cue = 0
position = 0
length = 0

# files and dirs
root_dir = "/mnt/usb/stems"
files = os.listdir(root_dir)
files.sort()
file_idx = 0
current = ""

def stems():
  d = root_dir+"/"+current
  return [os.path.join(d, f) for f in os.listdir(d)]

# CAD
cad = pifacecad.PiFaceCAD()
lcd = cad.lcd
lcd.clear()
lcd.backlight_on()

# OSC client
osc_client = OSC.OSCClient()
osc_client.connect(('127.0.0.1', 6449))   # localhost, port 57120

def osc_send(addr,param):
  osc_msg = OSC.OSCMessage()
  osc_msg.setAddress(addr)
  if type(param) is list:
    for p in param:
      osc_msg.append(p)
  else:
    osc_msg.append(param)
  osc_client.send(osc_msg)

# OSC server
osc_server = OSC.OSCServer(('127.0.0.1', 6448))

def set_position(path, tags, args, source):
  global position
  # tags will contain 'fff'
  # args is a OSCMessage with data
  # source is where the message came from (in case you need to reply)
  position = args[0]

def set_length(path, tags, args, source):
  global length
  length = args[0]

def run_server():
  while True:
    osc_server.handle_request()

osc_server.addMsgHandler("/current_position", set_position)
osc_server.addMsgHandler("/length", set_length)
thread.start_new_thread(run_server,())

# functions
def select(i):
  global file_idx
  file_idx = file_idx + i
  if file_idx < 0: file_idx = len(files)-1
  elif file_idx >= len(files): file_idx = 0

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

def goto(samples):
  osc_send("/abs_position",int(samples))

def bar(): # nr of samples in 1 bar 
  return 4*44100*60/original_bpm

def beat(): # nr of samples in 1 bar 
  return 44100*60/original_bpm

def move(samples):
  osc_send("/relative_position",int(samples))

def move_bars(bars):
  move(bars*bar())

def move_beats(beats):
  move(beats*beat())

def move_ms(ms):
  move(ratio*ms*44100/1000)

def current_pos():
  osc_msg = OSC.OSCMessage()
  osc_msg.setAddress("/get_position")
  osc_client.send(osc_msg)
  time.sleep(0.01) # wait for OSC to arrive

def set_cue():
  global cue
  current_pos()
  loop_nr = position // bar() # floor division
  cue = loop_nr*bar()

def time_format(i):
  seconds = i/44100.0/rate
  minutes = seconds//60
  seconds = seconds - 60*minutes
  return ('%02d' % int(minutes))+":"+('%02d' % int(round(seconds)))

def update_display():
  current_pos()
  lcd.clear()
  lcd.blink_off()
  lcd.set_cursor(0,0)
  lcd.write(files[file_idx])
  lcd.set_cursor(13,0)
  lcd.write(('%03d' % int(round(bpm))))
  lcd.set_cursor(0,1)
  lcd.write(time_format(length-position))
  lcd.set_cursor(11,1)
  lcd.write(time_format(cue))
  set_cursor()

def set_cursor():
  if mode == modes[0]:
    lcd.set_cursor(0,0)
    if files[file_idx] != current: lcd.blink_on()
  elif mode == modes[1]: lcd.set_cursor(13,0)
  elif mode == modes[3]: lcd.set_cursor(0,1)
  elif mode == modes[4]: lcd.set_cursor(11,1)

def select_mode(event):
  global mode
  mode = modes[event.pin_num]
  update_display()

def edit(event):
  if mode == modes[0]:
    if event.pin_num == 5:
      if cad.switches[0].value == 1: quit()
      else: load()
    elif event.pin_num == 6: select(-1)
    elif event.pin_num == 7: select(1)
  elif mode == modes[1]:
    #if event.pin_num == 5:
    if event.pin_num == 6:
      set_bpm(bpm-1)
    elif event.pin_num == 7:
      set_bpm(bpm+1)
  elif mode == modes[2]:
    if event.pin_num == 6:
      last_bpm = bpm
      while cad.switches[6].value == 1:
        set_bpm(0.9*bpm)
        time.sleep(0.5)
    elif event.pin_num == 7:
      last_bpm = bpm
      while cad.switches[7].value == 1:
        set_bpm(1.1*bpm)
        time.sleep(0.5)
    set_bpm(last_bpm)
  elif mode == modes[3]:
    if event.pin_num == 5: set_cue()
    elif event.pin_num == 6: move_bars(-8)
    elif event.pin_num == 7: move_bars(8)
  elif mode == modes[4]:
    if event.pin_num == 5: set_cue()
    elif event.pin_num == 6: goto(0)
    elif event.pin_num == 7: goto(cue)
  update_display()

def quit():
  cad.lcd.clear()
  cad.lcd.backlight_off()
  osc_server.close()
  os.system("poweroff")
    
listener = pifacecad.SwitchEventListener(chip=cad)
for i in range(5):
    listener.register(i, pifacecad.IODIR_ON, select_mode)

for i in range(5,8):
    listener.register(i, pifacecad.IODIR_ON, edit)

update_display()
listener.activate()

def update_time():
  while True:
    update_display()
    time.sleep(1)

#thread.start_new_thread(update_time,())
