#!/usr/bin/env python3

#
# picochat_server.py
# (c) 2022, Joshua Moore
#
# This is the WebSocket server supporting picochat, a PICO-8
# chat application built as an example using p8modem.
# This server-side code isn't actually specific to the PICO-8
# at all, and could be used as the backend for any simple WebSocket
# chat application.
# The first message sent by the client becomes that user's username,
# while each subsequent message is relayed to other connected clients.
#
# This program is free software licensed under the terms of the
# GNU GPLv3. See LICENSE.txt for details.
#

import json
import asyncio
import datetime
from websockets import serve

# message logging
MESSAGE_LOGGING = True
LOGFILE = "log.txt"

# name length restriction
MAX_NAME_LENGTH = 8
# message length restriction
MAX_MSG_LENGTH = 30

CONNS = { }


# return a string containing the packet data,
# without the leading length byte
def pktarr2str(pktarr):
    return ''.join([chr(v) for v in pktarr[1:MAX_MSG_LENGTH + 1]])


# convert string to ord byte array
def str2arr(msg):
    return [ord(v) for v in msg]


# write information about a user's message to the logfile
def msglog(user, msg):
    # current time
    logstr = f"{datetime.datetime.now().isoformat()}\n"
    # remote IP address
    logstr += f"{user[0].remote_address[0]}\n"
    # username
    logstr += f"{user[1]}\n"
    # message content
    logstr += f"{msg}\n"

    print(logstr, end='')
    with open(LOGFILE, "a") as logfile:
        logfile.write(logstr)


async def send_message(username, msg_str):
    # send normal formatted message
    out_str = username + ":\n  " + msg_str.replace("\n", "").replace("\t", "")
    await broadcast(out_str)


async def broadcast(msg):
    # placeholder packet length byte
    out_pkt = [ 0 ]

    # pack message
    out_pkt = out_pkt + str2arr(msg)

    # write final length to packet[0]
    out_pkt[0] = len(out_pkt)

    out_msg = json.dumps(out_pkt)
    for puid in CONNS:
        if CONNS[puid] is None:
            continue

        psock = CONNS[puid][0]
        if psock.open:
            await psock.send(out_msg)
        else:
            username = CONNS[puid][1]
            CONNS[puid] = None
            await broadcast(f"\n-- {username} left")


async def echo(sock, asdf):
    async for message in sock:
        pkt_arr = json.loads(message)
        pkt_str = pktarr2str(pkt_arr)
        
        uid = id(sock)
        if not uid in CONNS:
            # create client entry
            # [ socket, username ]
            username = pkt_str[0:MAX_NAME_LENGTH].replace("\n", "").replace("\t", "")
            # first message sent by the client is the username
            CONNS[uid] = [sock, username]
            await broadcast(f"\n++ {username} joined")
        else:
            if MESSAGE_LOGGING:
                msglog(CONNS[uid], pkt_str)
            username = CONNS[uid][1]
            await send_message(username, pkt_str)

    # clean up empty user entries
    for k, v in CONNS.items():
        if v is None:
            del CONNS[k]


if __name__ == '__main__':
    async def main():
        async with serve(echo, "0.0.0.0", 8888):
            await asyncio.Future()

    asyncio.run(main())
