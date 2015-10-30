SndBuf buffers[6];
for( 0 => int i; i < buffers.cap(); i++ ) { buffers[i] => dac.chan(i); }
0 => int loop_start;
0 => int loop_end;

OscRecv recv;
6449 => recv.port;
recv.listen();

OscSend xmit;
xmit.setHost("127.0.0.1", 6448);

recv.event( "/load, s s s s s s" ) @=> OscEvent files;
fun void load_listener() {
  while ( true ) {
    files => now;
    while ( files.nextMsg() != 0 ) { 
      for( 0 => int i; i < buffers.cap(); i++ ) { files.getString() => buffers[i].read; }
    }
  }
}
spork ~ load_listener();

recv.event( "/rate, f" ) @=> OscEvent rate;
fun void rate_listener() {
  while ( true ) {
    rate => now;
    while ( rate.nextMsg() != 0 ) { 
      rate.getFloat() => float r;
      for( 0 => int i; i < buffers.cap(); i++ ) { r => buffers[i].rate; }
    }
  }
}
spork ~ rate_listener();

recv.event( "/get_position" ) @=> OscEvent get_pos;
fun void get_pos_listener() {
  while ( true ) {
    get_pos => now;
    while ( get_pos.nextMsg() != 0 ) { 
      xmit.startMsg( "/current_position", "i" );
      buffers[0].pos() => xmit.addInt;
    }
  }
}
spork ~ get_pos_listener();

recv.event( "/abs_position, i" ) @=> OscEvent abs_pos;
fun void abs_position_listener() {
  while (true) {
    abs_pos => now;
    while ( abs_pos.nextMsg() != 0 ) { 
      abs_pos.getInt() => int p;
      for( 0 => int i; i < buffers.cap(); i++ ) { p => buffers[i].pos; }
    }
  }
}
spork ~ abs_position_listener();

recv.event( "/relative_position, i" ) @=> OscEvent pos;
fun void relative_position_listener() {
  while (true) {
    pos => now;
    while ( pos.nextMsg() != 0 ) { 
      pos.getInt() => int p;
      buffers[0].pos() +=> p;
      for( 0 => int i; i < buffers.cap(); i++ ) { p => buffers[i].pos; }
    }
  }
}
spork ~ relative_position_listener();


while (true) {
  1::second => now;
  //xmit.startMsg( "/current_position", "i" );
  //buffers[0].pos() => xmit.addInt;
}
