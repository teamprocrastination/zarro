#!/usr/bin/env python
# coding=utf-8

# Original from http://code.activestate.com/recipes/491264/
# I used input from Andrei Fokau on this particular script as well.


import argparse
import datetime
import sys
import time
import threading
import traceback
import socketserver
import struct
import os
import pwd
import getpass
try:
    from dnslib import *
except ImportError:
    print("Missing dependency dnslib: <https://pypi.python.org/pypi/dnslib>. Please install it with `pip`.")
    sys.exit(2)


ipdictionary = {}

class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)


# CONFIGURATION
D = DomainName('your.domain.')      # Domain under your control, ends with a .
IP = '8.8.8.8'                      # Your external webserver address
GWIP = '192.168.178.1'              # Ziggo default
TTL = 1
CHROOTDIR = "/home/hacktheplanet/"  # The DNS server will chroot to here. Please perform
                                    #   echo 0 > $CHROOTDIR/Chroot\ succeeded
                                    #   chown www-user:www-user $CHROOTDIR/Chroot\ succeeded
USER = "hacktheplanet"              # The user to which privileges are dropped
# CONFIGURATION END: hostname is now fixed on router but can be configurable as well

soa_record = SOA(
    mname=D.ns1,  # primary name server
    rname=D.raymond,  # email of the domain administrator
    times=(
        20190720,  # serial number
        1,  # refresh
        3,  # retry
        1,  # expire
        1,  # minimum
    )
)
ns_records = [NS(D.ns1), NS(D.ns2)]
records = {
    D: [A(IP), AAAA((0,) * 16), MX(D.mail), soa_record] + ns_records,
    D.ns1: [A(IP)],  # MX and NS records must never point to a CNAME alias (RFC 2181 section 10.3)
    D.ns2: [A(IP)],
    D.mail: [A(IP)],
    D.router: [A(IP)],
    D.erouter: [A(IP)],
    D.irouter: [A(GWIP)],
    D.www: [A('8.8.8.8')],
    D.raymond: [CNAME(D)],
}


def dns_response(data,rqIP):
    request = DNSRecord.parse(data)

    # print(request)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]

    if qn == D or qn.endswith('.' + D):
        # HBR: here we mess around with the IP addresses
        # If the hostname is our target, we open the file /Chroot\ succeeded in the chrooted environment
        # in our case that's /home/hacktheplanet/Chroot\ succeeded
        # in case the file contains a 1, we redirect
        # The value is set by the php scripts switch-on.php and switch-off.php.
        print("Request from %s, hostname %s" % (rqIP,qn))
        if qn == 'router.hacktheplanet.ga.':
            f = open("/Chroot succeeded", "r")
            a = f.read()
            if a == "1":
                print "Routed to the internal Router IP"
                qn = 'irouter.hacktheplanet.ga.'
            else:
                print "Routed to external Router IP"
        for name, rrs in records.items():
            if name == qn:
                for rdata in rrs:
                    rqt = rdata.__class__.__name__
                    if qt in ['*', rqt]:
                        reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=TTL, rdata=rdata))

        for rdata in ns_records:
            reply.add_ar(RR(rname=D, rtype=QTYPE.NS, rclass=1, ttl=TTL, rdata=rdata))

        reply.add_auth(RR(rname=D, rtype=QTYPE.SOA, rclass=1, ttl=TTL, rdata=soa_record))

    # print("---- Reply:\n", reply)

    return reply.pack()


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        # print("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0], self.client_address[1]))
        try:
            data = self.get_data()
            # print(len(data), data)  # repr(data).replace('\\x', '')[1:-1]
            # HBR: We have to add client IP
            self.send_data(dns_response(data,self.client_address[0]))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class TCPRequestHandler(BaseRequestHandler):

    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def main():
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python.')
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python. Usually DNSs use UDP on port 53.')
    parser.add_argument('--port', default=53, type=int, help='The port to listen on.')
    parser.add_argument('--tcp', action='store_true', help='Listen to TCP connections.')
    parser.add_argument('--udp', action='store_true', help='Listen to UDP datagrams.')
    
    args = parser.parse_args()
    if not (args.udp or args.tcp): parser.error("Please select at least one of --udp or --tcp.")

    print("Starting nameserver...")

    servers = []
    if args.udp: servers.append(socketserver.ThreadingUDPServer(('', args.port), UDPRequestHandler))
    if args.tcp: servers.append(socketserver.ThreadingTCPServer(('', args.port), TCPRequestHandler))
    # HBR making the application a bit more safe by reducing privileges and chrooting the process
    pw  = pwd.getpwnam(USER)
    uid = pw.pw_uid
    print "Chroot into "+CHROOTDIR
    os.chroot(CHROOTDIR)
    for f in os.listdir("/"): 
        print f
    print "Dropping privileges"
    os.setuid(uid)
    print("Current user ID: %s" % (os.getuid()))

    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        print("%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name))

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()

if __name__ == '__main__':
    main()

