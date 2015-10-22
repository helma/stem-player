//if( me.args() ) me.arg(0) => filename;
SndBuf b0 => dac.chan(0); 
SndBuf b1 => dac.chan(1);
SndBuf b2 => dac.chan(2); 
SndBuf b3 => dac.chan(3);
SndBuf b4 => dac.chan(4); 
SndBuf b5 => dac.chan(5);
"132magnet_drums_l.wav" => b0.read;
"132magnet_drums_r.wav" => b1.read;
"132magnet_bass_l.wav" => b2.read;
"132magnet_bass_r.wav" => b3.read;
"132magnet_music_l.wav" => b4.read;
"132magnet_music_r.wav" => b5.read;

OscRecv recv;
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/rate, f" ) @=> OscEvent rate;
recv.event( "/position, f" ) @=> OscEvent pos;

fun void rate_listener() {
  while ( true ) {
      // wait for event to arrive
      rate => now;
      // grab the next message from the queue. 
      while ( rate.nextMsg() != 0 ) { 
          rate.getFloat() => float r;
          r => b0.rate;
          r => b1.rate;
          r => b2.rate;
          r => b3.rate;
          r => b4.rate;
          r => b5.rate;
      }
  }
}

fun void position_listener() {
  while (true) {
    pos => now;
    while ( pos.nextMsg() != 0 ) { 
        pos.getFloat() $ int  => int p;
        <<< p >>>;
        p => b0.pos;
        p => b1.pos;
        p => b2.pos;
        p => b3.pos;
        p => b4.pos;
        p => b5.pos;
    }
  }
  <<< b0.pos() >>>;
}

spork ~ rate_listener();
spork ~ position_listener();
while (true) { 1::second => now; }
