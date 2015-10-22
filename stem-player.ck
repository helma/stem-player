SndBuf buffers[6];
for( 0 => int i; i < buffers.cap(); i++ ) { buffers[i] => dac.chan(i); }

OscRecv recv;
6449 => recv.port;
recv.listen();

recv.event( "/rate, f" ) @=> OscEvent rate;
recv.event( "/position, i" ) @=> OscEvent pos;
recv.event( "/load, s s s s s s" ) @=> OscEvent new_files;

fun void load_listener() {
  while ( true ) {
    new_files => now;
    while ( new_files.nextMsg() != 0 ) { 
      for( 0 => int i; i < buffers.cap(); i++ ) { new_files.getString() => buffers[i].read; }
    }
  }
}

fun void rate_listener() {
  while ( true ) {
    rate => now;
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

spork ~ load_listener();
spork ~ rate_listener();
spork ~ position_listener();
while (true) { 1::second => now; }
