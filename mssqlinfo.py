#!/usr/bin/env python
"""mssqlinfo: (c) 2006-2009 Philipp Wolfer

About:
This module enables access to a SQL server browser
which provides information about named MS-SQL server
instances.

The SQL server browser listens on port 1434 and provides
information such as the port number a named instance is
using.

This module may be used from the command line. See
the documentation of the main function for further details.

License:
mssqlinfo is Copyright (c) 2006 Philipp Wolfer.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the RBrainz project nor the names of the
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__version__ = '0.1.2'

import socket
import sys

DEFAULT_INSTANCE_NAME = 'MSSQLSERVER'
DEFAULT_SERVER_BROWSER_PORT = 1434
DEFAULT_SERVER_BROWSER_HOST = 'localhost'

def getInstanceInfo(servername, instance, port = DEFAULT_SERVER_BROWSER_PORT):
    """Retrieve information about a named MS-SQL instance
    running on servername.

    Returns a dictionary containing the information."""

    sqlServerBrowser = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sqlServerBrowser.connect((servername, port))
    sqlServerBrowser.settimeout(10)

    request = "%c" % 0x04 + instance
    sqlServerBrowser.send(request)
    response = sqlServerBrowser.recv(1024)[3:]
    sqlServerBrowser.close()

    infoList = response.split(";")
    infoDict = dict()
    for i in range(0, len(infoList)-1, 2):
        if (infoList[i] != ''):
            infoDict[infoList[i]] = infoList[i+1]
        
    return infoDict

def usage():
    """Print help for command line usage."""
    print main.__doc__

def main(argv):
    """mssqlinfo: (c) 2006 Philipp Wolfer

Retrieves information about a named MS-SQL instance. This requires
that the SQL Server Browser is running on the server.
  -h --host        Hostname
                   Defaults to \"localhost\"
  -i --instance    Instance name
                   Defaults to MSSQLSERVER.
  -p --port        Port of the SQL server browser.
                   Defaults to 1434.
     --value=VALUE If set only the specified value will be
                   returned. Value can be one of ServerName,
                   InstanceName, IsClustered, Version, tcp,
                   nt or via.
     --help        Display this help and exit.
     --version     Display version information and exit.

Example: mssqlinfo -hlocalhost -iSQLEXPRESS"""

    import getopt
    shortArgs = "h:i:p:"
    longArgs = ["host=", "instance=", "port=", "value=", "help", "version"]
    
    try:
        opts, args = getopt.getopt(argv, shortArgs, longArgs)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    instance = DEFAULT_INSTANCE_NAME
    port = DEFAULT_SERVER_BROWSER_PORT;
    hostname = DEFAULT_SERVER_BROWSER_HOST;
    value = None
    
    for opt, arg in opts:
        if opt == "--help":
            usage()
            sys.exit()
        elif opt == "--version":
            print "mssqlinfo %s" % __version__
            sys.exit()
        elif opt in ("-h", "--host"):
            hostname = arg
        elif opt in ("-i", "--instance"):
            instance = arg
        elif opt in ("-p", "--port"):
            port = int(arg);
        elif opt == "--value":
            value = arg;

    try:
        info = getInstanceInfo(hostname, instance, port)
    except socket.error, msg:
        sys.stderr.write("Connection to %s failed: %s." % (hostname, msg))
        sys.exit(1)

    if (value == None):
        print "\n".join(["%s = %s" % (k, v) for k, v in info.items()])
    else:
        try:
            print info[value]
        except KeyError:
            sys.exit(1)
    
    sys.exit()
    
if __name__ == "__main__":
    main(sys.argv[1:])
