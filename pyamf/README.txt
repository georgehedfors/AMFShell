PyAMF provides Action Message Format (AMF) support for Python that is
compatible with the Adobe Flash Player. It includes integration with Python
web frameworks like Django, Pylons, Twisted, SQLAlchemy and more.

The Adobe Integrated Runtime and Adobe Flash Player use AMF to communicate
between an application and a remote server. AMF encodes remote procedure calls
(RPC) into a compact binary representation that can be transferred over
HTTP/HTTPS or the RTMP/RTMPS protocol. Objects and data values are serialized
into this binary format, which increases performance, allowing applications to
load data up to 10 times faster than with text-based formats such as XML or
SOAP.

AMF3, the default serialization for ActionScriptª 3.0, provides various
advantages over AMF0, which is used for ActionScriptª 1.0 and 2.0. AMF3 sends
data over the network more efficiently than AMF0. AMF3 supports sending int
and uint objects as integers and supports data types that are available only
in ActionScriptª 3.0, such as ByteArray, ArrayCollection, and ObjectProxy.
