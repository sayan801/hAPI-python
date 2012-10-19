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
Displays the instantiation status of one or more VMs, typically
being one of QUEUED, IN_PROCESS, SUCCEEDED or FAILED.
'''

import hapi
import sys

ACCESS_KEY="XXXXXXXXXXXXXXXX"
ACCESS_SECRET="XXXXXXXXXXXXXXXXXX"
hAPI = hapi.Client(ACCESS_KEY, ACCESS_SECRET)

labels = sys.argv[1:]
for label in labels:
  try:  
    device_id = hAPI.id_from_label(label)
    result = hAPI.voxel.voxcloud.status(device_id = device_id)
    print "Status for %s(%s): %s" % (label, device_id, result.devices.device.status)
  except Exception, e:
    print e
