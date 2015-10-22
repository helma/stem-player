#!/bin/env python2
import pifacecad
import sys
import OSC
osc_client = OSC.OSCClient()
osc_client.connect(('127.0.0.1', 6449))   # localhost, port 57120
osc_msg = OSC.OSCMessage()

bpm = 132.0
original_bpm = 132.0
rate = bpm/original_bpm

# TODO read tracks, format, export?
# track list

def osc_send(addr,param):
  osc_msg.setAddress(addr)
  if type(param) is list:
    for p in params:
      osc_msg.append(p)
  else:
    osc_msg.append(param)
  osc_client.send(osc_msg)

def load (files):
  # TODO set original_bpm
  osc_send("/load",files)
  bpm(bpm)

def bpm(new_bpm):
  bpm = new_bpm
  rate = bpm/original_bpm
  osc_send("/rate",rate)

def move(samples):
  osc_send("/position",samples)

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
  #loop_dur = loop_size/44100/ratio
  loop_nr = current_pos() // loop_size # floor division
  start = loop_nr*loop_size
  osc_send("/loop",start,loop_size)

def noloop():
  osc_send("/loop",0,0)
