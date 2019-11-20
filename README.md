# Peer to Peer system with a Distributed Index
20th November, 2019

# Language used:
- Python 3.7

# Description:

  - The project delivers a peer to peer file sharing system which runs over TCP.
  - This is very similar to how Bittorrent works. There are peers and there is a central regristration server.
  - The registration server(RS) listens on a well known port. Everytime a peer wants to be a part of the file sharing network, the peer needs to register with the registration server.
  - Keepalives are maintained for the peers at the registration server.
  - When a peer wants to request files or send files, it requests for the current list of active peers from the RS and begins requesting the required file from the peers in a round robin fashion. This is done by querying the other peer for the list of files it currently holds.
  - Every peer updates the current list of files it holds everytime it receives a file.
  - All of these communication happens in parallel with the help of multithreading. The RS and the peers exchange data with the help of socket modules in python.

# Usage:
  - There are three codes - rs_server.py, p2p_client.py and peer_server.py
  - The rs_server.py is the RS server's implementation
  - Since every peer acts as a client and as a server, there are two scripts for it.

# Version:
 - stable_1.0

Authors
----
Shrikanth Sudhersan, Dhanraj Vedanth Raghunathan

-- --
This project was a part of the course Internet Protocol (ECE573)
-- -- 
