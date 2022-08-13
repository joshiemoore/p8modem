//
// p8modem.js
//
// "Virtual modem" implementation of p8modem.
// This module acts as the bridge between the p8modem's Lua
// firmware API and the underlying WebSocket connection.
// The Lua API cooperates with the "virtual hardware" implementation
// in this file for the purposes of transferring data between the
// PICO-8 and the JS context across the GPIO memory interface.
//
// To use p8modem, export your PICO-8 program as a web application,
// then add a script tag to the HTML file which uses this script
// as its src. Then change SOCKET_URL below to point to the desired
// WebSocket URL.
// Once you've done that, you will be able to send and receive
// packets to and from the WebSocket server by including the Lua API
// from "p8modem.lua".
// See the documentation for more information.
//
// (c) 2022, Joshua Moore
// This program is free software, licensed under the terms
// of the GNU GPLv3. See LICENSE.txt for details.
//

// replace this with the WebSocket URL you want to connect to
const SOCKET_URL = "ws://localhost:8888";

// incoming packet queue
const _p8m_queue = new Array();


// pop a packet from the rx queue and write it to GPIO memory
const p8m_rx = () => {
  // receive incoming packet
  const packet = _p8m_queue.shift();

  if (packet !== undefined) {
    // write -1 to GPIO[0], indicating that we are processing an rx packet
    pico8_gpio[0] = 255;

    // convert packet length to a negative signed byte
    const plen = packet[0];
    const plen_signed = (128 - plen) | 0x80;

    for (let i = 1; i < plen; i++) {
        pico8_gpio[i] = packet[i];
    }

    // write negative packet length to GPIO[0]
    // this signals to the PICO-8 that there is an incoming
    // packet available to be read
    pico8_gpio[0] = plen_signed;
  }
};


// read a packet from GPIO memory and send it to the server
const p8m_tx = () => {
  // read outgoing packet
  const tx_packet = new Array();
  const plen = pico8_gpio[0];
  tx_packet.push(plen);
  for (let i = 1; i < plen; i++) {
    tx_packet.push(pico8_gpio[i]);
  }

  // send packet array in JSON array format
  socket.send("[" + tx_packet + "]");

  // finally write 0 to GPIO[0],
  // freeing GPIO memory for further use
  pico8_gpio[0] = 0;
};


// handle incoming/outgoing packets
const p8m_update = () => {

  if (pico8_gpio[0] !== 0) {
    // data is present on GPIO memory
    const plen = pico8_gpio[0];

    if (plen > 1 && plen < 128) {
      // send outgoing packet
      p8m_tx();
    }
  }

  if (!pico8_gpio[0]) {
    // GPIO memory is free, receive next incoming packet
    p8m_rx();
  }
};


// prepare websocket
const socket = new WebSocket(SOCKET_URL);

socket.onopen = (e) => {
  setInterval(p8m_update, 10);
};

socket.onmessage = (e) => {
  const rx_packet = JSON.parse(e.data);
  _p8m_queue.push(rx_packet);
};

socket.onclose = (e) => {
  alert("p8modem has lost connection");
};
