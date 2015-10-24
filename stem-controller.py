#!/bin/env python2
import pifacecad
import sys, time, os, re, thread
import OSC

# global variables
modes = ["bpm","select","nudge","bars","cue"]
mode = modes[1]
bpm = 132.0
original_bpm = 132.0
rate = bpm/original_bpm
cue = 0
position = 0

# files and dirs
root_dir = "/mnt/usb/stems"
files = os.listdir(root_dir).sort()
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

def run_server():
  while True:
    osc_server.handle_request()

osc_server.addMsgHandler("/current_position", set_position)
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

def set_cue():
  global cue
  current_pos()
  time.sleep(0.01) # wait for OSC to arrive
  loop_nr = position // bar() # floor division
  cue = loop_nr*bar()

'''
def loop(bars):
  loop_size = bars*bar()
  loop_nr = current_pos() // loop_size # floor division
  start = loop_nr*loop_size
  osc_send("/loop",start,loop_size)

def noloop():
  osc_send("/loop",0,0)
'''

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
  else:
    lcd.write(" "+mode)

def select_mode(event):
  global mode
  mode = modes[event.pin_num]
  update_display()

def quit():
  # TODO kill chuck?
  osc_server.close()
  listener.deactivate()
  sys.exit()
  # poweroff


def edit(event):
  if mode == modes[0]:
    if event.pin_num == 6: set_bpm(bpm-1)
    elif event.pin_num == 7: set_bpm(bpm+1)
  elif mode == modes[1]:
    if event.pin_num == 5: load()
    elif event.pin_num == 6: select(-1)
    elif event.pin_num == 7: select(1)
  elif mode == modes[3]:
    if event.pin_num == 5: set_cue()
    elif event.pin_num == 6: move_bars(-8)
    elif event.pin_num == 7: move_bars(8)
  elif mode == modes[4]:
    if event.pin_num == 5: set_cue()
    elif event.pin_num == 6: goto(0)
    elif event.pin_num == 7: goto(cue)
  update_display()
    
listener = pifacecad.SwitchEventListener(chip=cad)
for i in range(5):
    listener.register(i, pifacecad.IODIR_ON, select_mode)

for i in range(5,8):
    listener.register(i, pifacecad.IODIR_ON, edit)

update_display()
listener.activate()

