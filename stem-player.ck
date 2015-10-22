//if( me.args() ) me.arg(0) => filename;
SndBuf buffers[6];
for( 0 => int i; i < buffers.cap(); i++ ) { buffers[i] => dac.chan(i); }
[ "132magnet_drums_l.wav",
  "132magnet_drums_r.wav",
  "132magnet_bass_l.wav",
  "132magnet_bass_r.wav",
  "132magnet_music_l.wav",
  "132magnet_music_r.wav"
] @=> string files[];
for( 0 => int i; i < files.cap(); i++ ) { files[i] => buffers[i].read; }

OscRecv recv;
6449 => recv.port;
// start listening (launch thread)
recv.listen();

// create an address in the receiver, store in new variable
recv.event( "/rate, f" ) @=> OscEvent rate;
recv.event( "/position, i" ) @=> OscEvent pos;
//recv.event( "/load, f" ) @=> OscEvent pos;

fun void rate_listener() {
  while ( true ) {
    // wait for event to arrive
    rate => now;
    // grab the next message from the queue. 
    while ( rate.nextMsg() != 0 ) { 
      rate.getFloat() => float r;
      for( 0 => int i; i < buffers.cap(); i++ ) { r => buffers[i].rate; }
    }
  }
}

fun void position_listener() {
  while (true) {
    pos => now;
    while ( pos.nextMsg() != 0 ) { 
      pos.getInt() => int p;
      for( 0 => int i; i < buffers.cap(); i++ ) { p => buffers[i].pos; }
    }
  }
}

spork ~ rate_listener();
spork ~ position_listener();
while (true) { 1::second => now; }
