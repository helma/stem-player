SndBuf buffers[6];
for( 0 => int i; i < buffers.cap(); i++ ) { buffers[i] => dac.chan(i); }
0 => int loop_start;
0 => int loop_end;

OscRecv recv;
6449 => recv.port;
recv.listen();

recv.event( "/rate, f" ) @=> OscEvent rate;
recv.event( "/position, i" ) @=> OscEvent pos;
recv.event( "/loop, i i" ) @=> OscEvent loop;
recv.event( "/load, s s s s s s" ) @=> OscEvent files;

fun void load_listener() {
  while ( true ) {
    files => now;
    while ( files.nextMsg() != 0 ) { 
      for( 0 => int i; i < buffers.cap(); i++ ) { files.getString() => buffers[i].read; }
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
      buffers[0].pos() +=> p;
      for( 0 => int i; i < buffers.cap(); i++ ) { p => buffers[i].pos; }
    }
  }
}

fun void loop_listener() {
  while (true) {
    loop => now;
    while ( loop.nextMsg() != 0 ) { 
      loop.getInt() => loop_start;
      loop.getInt() => loop_end;
    }
  }
}

spork ~ load_listener();
spork ~ rate_listener();
spork ~ position_listener();
spork ~ loop_listener();

while (true) {
  1::samp => now;
  if (loop_end != 0 && buffers[0].pos() >= loop_end) {
    for( 0 => int i; i < buffers.cap(); i++ ) { loop_start => buffers[i].pos; }
  }
}
