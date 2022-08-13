--
-- p8modem.lua
--
-- "Firmware" for p8modem, the virtual PICO-8 modem.
-- #include this file in your own PICO-8 programs in order
-- to use the p8modem API to send/receive packets over WebSockets.
-- See the documentation for more information.
--
-- (c) 2022 Joshua Moore
-- This program is free software, licensed under the terms
-- of the GNU GPLv3. See LICENSE.txt for details.
--


-- address of the first byte of PICO-8's 128-byte GPIO
-- memory space
-- the GPIO memory is used to transfer packet data between
-- the JS "hardware" and Lua "firmware"
_gpio_base = 0x5f80


-- transmit a packet to the websocket modem over the GPIO interface
-- buf should be a byte array or stringcontaining the desired tx packet data
--   buf should be at most 127 bytes long
--   bytes after the 127th will be ignored
-- returns the actual number of bytes sent
function p8m_send(buf)
  -- write 1 to GPIO[0] to signal that an outgoing packet
  -- is being prepared
  poke(_gpio_base, 1)

  -- write packet data to GPIO memory
  txcount = 0
  for i = 1, #buf do
    -- packet data is limited to 127 bytes
    if i > 127 then
      break
    end

    -- handle both strings and byte arrays
    if type(buf) == "string" then
      -- unpack string into GPIO memory
      poke(_gpio_base + i, ord(sub(buf, i, i)) & 0xff)
    elseif type(buf) == "table" then
      -- unpack byte array into GPIO memory
      poke(_gpio_base + i, buf[i] & 0xff)
    -- else
    -- unsupported type - silently ignore packet
    end

    txcount = txcount + 1
  end

  -- increment once more to account for packet length byte
  txcount = txcount + 1

  -- finally, write total packet length to GPIO[0]
  -- this signals to the modem that there is a packet ready to send
  poke(_gpio_base, txcount)

  return txcount
end


-- read a packet from GPIO memory, returning a byte array
-- containing only the packet data (without the leading packet
-- length byte)
-- returns nil if there is no rx packet waiting to be read
function p8m_recv()
  plen = peek(_gpio_base)

  -- if there is an unsent tx packet in GPIO memory,
  -- do not overwrite it with an rx packet
  if plen < 128 then
    return nil
  end

  -- convert signed negative length to positive value
  plen = (128 - plen) & 0x7f

  -- deserialize incoming packet
  packet = { }
  for i = 1, plen - 1 do
    add(packet, peek(_gpio_base + i))
  end

  -- write 0 to to GPIO[0]
  -- this signals that we are done reading the incoming packet,
  -- freeing GPIO memory
  poke(_gpio_base, 0)

  return packet
end
