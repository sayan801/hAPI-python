#!/usr/bin/env python
# Copyright 2010-2012 Internap Network Services Corporation and Mochila
# Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
This script reports the various devices within a Voxel 
infrastructure. Options exist to filter out devices,
or to change the type of information reported.

-t and -m look for the phrase that follows in either
the device type or the device model respectively (case-
insensitively). Thus, -m cloud would find all devices 
with 'cloud' in their model, such as those that have a
model of 'VoxCLOUD'.

By default, list reports the status of the VM (on/off/etc).
By specifying -s, the it will report the output of the
'status' command, which reports a devices invocation state,
e.g. QUEUED, IN_PROGRESS, SUCCEEDED, FAILED

-v specifies 'verbose' output. This asks hAPI for verbose
output, and then simply prints the result to the screen
with no special formatting.
'''

import hapi
from optparse import OptionParser
import sys

usage = "%s [-t <TYPE>] [<HOST>...]" % sys.argv[0]
parser = OptionParser(usage)

parser.add_option("-t", "--type", dest="type", default=None,
                  help="Show only hosts who's type contains this")
parser.add_option("-m", "--model", dest="model", default=None,
                  help="Show only hosts who's model contains this")
parser.add_option("-n", "--host", dest="host", default=None,
                  help="Show just a single host")
parser.add_option("-s", "--show-status", dest="status", default=False,
                  action="store_true", 
                  help="show status if a voxCLOUD host")
parser.add_option("-v", "--verbose", dest="verbose", default=False,
                  action="store_true",
                  help="Show all details about devices")
(options, args) = parser.parse_args()
labels = args

ACCESS_KEY="XXXXXXXXXXXXXXXX"
ACCESS_SECRET="XXXXXXXXXXXXXXXXXX"
hAPI = hapi.Client(ACCESS_KEY, ACCESS_SECRET)

def tab(device, field, width):
  if device is None:
    print "%s%s" % (field.upper(), " " * (width-len(field))),
  elif hasattr(device, field):
    print "%s%s" % (device[field], " " * (width-len(device[field]))),
  else:
    print " " * width,

tab(None, "id", 6)
tab(None, "label", 25)
tab(None, "type", 15)
tab(None, "model", 22)
tab(None, "status", 10)
print

if options.verbose:
  verbosity="extended"
else:
  verbosity="normal"

result = hAPI.voxel.devices.list(verbosity = verbosity)

for device in result.devices.device:
  if options.model and options.model.upper() not in device.model.text.upper():
    continue
  if options.type and options.type.upper() not in device.type.text.upper():
    continue
  if options.host and options.host.upper() not in device.label.upper():
    continue
  if options.status and device.model.text == "VoxCLOUD":
    result = hAPI.voxel.voxcloud.status(device_id = device.id)
    device.status = result.devices.device.status

  if hasattr(device, "label"):
    dotpos = device.label.find(".")
    if dotpos>0:
      device.label = device.label[:dotpos]
  if hasattr(device, "type"):
    device.type = device.type.text
  if hasattr(device, "model"):
    device.model = device.model.text
  tab(device, "id", 6)
  tab(device, "label", 25)
  tab(device, "type", 15)
  tab(device, "model", 22)
  tab(device, "status", 10)
  print
  if options.verbose:
    print device
    print

