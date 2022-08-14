# p8modem
p8modem is a general-purpose WebSocket "modem" for PICO-8. You can use it to write PICO-8
programs which interact with WebSocket servers, in order to make multiplayer games,
chat programs, BBS services, or other networked software.

[Click this link](http://p8modem.net/picochat/) to access picochat, a basic chat program
implemented using p8modem.

p8modem is free software licensed under the terms of the GNU GPLv3. See LICENSE.txt
for details.

## PICO-8 Developer Guide - Use p8modem in your own programs!
To use p8modem in your own programs, you must deploy your program as a web application
and include `p8modem.js` in the generated HTML. Here are a list of steps you can follow:

1. Write a PICO-8 program using the p8modem API. For example, here is a simple program
   that just sends "Hello World!" over the WebSocket connection:

```
-- include the p8modem API
#include p8modem.lua

function _init()
  p8m_send("Hello World!")
end
```

2. Save the program as `helloworld.p8`.
3. Copy `p8modem.lua` from this repository to the directory containing your
   new program so that the p8modem Lua API can be included. On Linux, your
   PICO-8 carts will be found under `~/.lexaloffle/pico-8/carts/`
4. Copy `p8modem.js` from this repository to the same directory you copied
   `p8modem.lua` to in the previous step.
5. Open your copy of `p8modem.js` in a text editor. Change `SOCKET_URL` to a
   URL that points to the WebSocket server you're communicating with.
6. Now export your program as a web application from within PICO-8:
   `> EXPORT HELLOWORLD.HTML`
7. Open `helloworld.html` in a text editor, scroll to the bottom, and insert
   this line:
   
   `<script type="text/javascript" src="p8modem.js"></script>`
   
   right below the comment that says `<!-- Add content below the cart here -->`.
8. Finally, open `helloworld.html` in a web browser, and when you run the cart,
   your PICO-8 program will send the message `Hello World!` to the WebSocket
   server.

   If the message `p8modem has lost connection` appears, this means that you have
   entered the wrong URL for `SOCKET_URL` in `p8modem.js`, or the WebSocket server
   is not running.

If you would like to move your final application elsewhere, for example to deploy
it to a web server, just make sure that you keep `helloworld.html`, `helloworld.js`,
and `p8modem.js` all in the same directory. Replace `helloworld` with whatever you
named your program. You do not need to copy `p8modem.lua` to your web server.

Implementing your server-side WebSocket code is left as an exercise for the
reader, but you can find examples in the `examples/` directory.

Please see the `Limitations` section for items to note while using p8modem
to develop networked PICO-8 programs. Feel free to open an issue if you
have problems integrating p8modem into your own code.

### API Reference

These functions are available via `p8modem.lua` for developers to interact with p8modem
in order to communicate with a WebSocket server.

* `p8m_send(buf)` - Send a packet to the server. `buf` can either be a string
  or an array of bytes. Packet data is limited to 127 bytes in size.

* `p8m_recv()` - If there is a received packet available to be read, this
  function returns an array of bytes containing the packet data. The returned
  byte array will contain at maximum 127 bytes. If there is no incoming
  packet available to be read, this function returns `nil`.

  Received packets are stored in a queue by p8modem, so they will be available
  to be read as the GPIO buffer is available.

## Limitations
* p8modem only works when your PICO-8 program is deployed as a web application,
  and will not work when deployed via other methods. This is because p8modem
  uses JavaScript to access the PICO-8's GPIO memory and relay data over the
  WebSocket connection.
* Packet data sent with `p8m_send()` is limited to 127 bytes in size.
* Operations for sending and receiving packets both share the same buffer
  in GPIO memory. Sending takes priority over receiving, so if you call
  `p8m_send()` without first calling `p8m_recv()` to see if there is a packet
  available to be read, the received packet will be lost.
* p8modem will not work in cases where very-rapid communication is needed.
  Sending more than one packet per frame will currently not work in most cases,
  though future versions of p8modem may address this issue.
