#!/usr/local/bin/python2.7
# encoding: utf-8
'''
pingfromall -- ping a destination from all active interfaces

pingfromall is a small tool that pings a single destination IP from all active interfaces on the machine.

@author:     Oliver Thomas

@copyright:  2015 Oli's tools ltd. All rights reserved.

@license:    GNU

@contact:    oliver.thomas@teleconvergence.co.uk
@deffield    updated: 29-01-2015
'''

import sys
import os
import re
import socket
from SysEnvironment import SysEnvironment
import pyping

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2015-01-29'
__updated__ = '2015-01-29'

DEBUG = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    
    ipv4 = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2015 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("destination", help="The destination to ping")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        
        # Process arguments
        args = parser.parse_args()
        destination = args.destination
        if not ipv4.match(destination):
            try:
                destination = socket.gethostbyname(destination)
            except socket.gaierror as e:
                parser.error("\nUnknown host: %s (%s)\n" % (destination, e.args[1]))
        if DEBUG: print args
        
        
        
        # Now do it!
        go_do_it(destination)
        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    
    
def go_do_it(destination):
    env = SysEnvironment()
    addresses = env.get_interfaces_dict()
    pingers = {}
    count = 0
    for interface, address in addresses.items():
        count += 1
        # if DEBUG: print "\ninterface\t%s\thas address\t%s" % (interface, addresses[interface])
        this_id = "Testing %s" % (interface)
        pinger = pyping.Ping(destination, this_id, quiet_output=False, sourceaddress=address)
        pingers.update({interface : pinger})
    
    header = "\nTesting to %s from %d interfaces. Hit Ctrl+C to stop...\n" % (destination, count)
    while True:
        results = list()
        # Get the results...
        for interface, pinger in sorted(pingers.items()):
            results.append(pinger.do())
        # Clear the screen...
        os.system('cls' if os.name == 'nt' else 'clear')
        # Then print the results...
        print (header)
        for result in results:
            print (result)


    
if __name__ == "__main__":
    sys.exit(main())
