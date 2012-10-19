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
A DictObject is an object that is both an object and a dictionary.

Thus, foo["abc"] and foo.abc access the same thing.

This DictObject goes one step further than this, allowing the
provision of either json or XML when creating the object. Clearly,
XML and JSON are nested structures. Similarly, the resulting 
DictObject will be a nested object graph. Thus, taking an XML such as:

<result>
  <devices>
    <device id="1233" name="abcdef">Central Database Server</device>
  </devices>
</result>

You will be able to iterate over the result like so:

for device in result.devices.device:
  print device.id
  print device.name
  print device.text

'''
class DictObject(dict):
  def __init__(self, d = None, xml = None, json = None, xpath = None):
    if d:
      dict.__init__(self, d)
    else:
      dict.__init__(self)
    self.__dict__ = self
    
    if json is not None:
      for key, val in json.items():
        if isinstance(val, dict):
          val = DictObject(json=val)
        self[key]=val
    if xpath is not None and xml is not None:
      xml = xml.xpath(xpath)
    if xml is not None:
      if not isinstance(xml, list):
        xml = [xml]
      for node in xml:
        for attrib in node.attrib:
          self[attrib] = node.attrib[attrib]
        for child in node.getchildren():
          if len(child.attrib)==0 and len(child.getchildren())==0:
            self[child.tag]=child.text
          elif self.has_key(child.tag) and isinstance(self[child.tag], list):
            self[child.tag].append(DictObject(xml=child))
          elif self.has_key(child.tag):
            self[child.tag] = [self[child.tag], DictObject(xml=child)]
          else:
            self[child.tag] = DictObject(xml = child)
        if len(node.attrib)==0 and len(node.getchildren())==0:
          self[node.tag]=node.text
        elif node.text:
          self.text=node.text

  def __getitem__(self, name):
    if dict.has_key(self, name):
      return dict.__getitem__(self, name)
    else:
      return ""

  def __str_(self, indent = 0):
  
    s = ""
    s+= " " * indent
    s+= "{\n"
    indent +=2
    for key, val in self.__dict__.items():
      if isinstance(val, DictObject):
        s+= " " * indent
        s+=key
        s+=" = \n"
        s+= val.__str__(indent+2)
      elif isinstance(val, list):
        s+= " " * indent
        s+= key
        s+= " = [\n"
        for x in val:
          s+= " " * (indent+2)
          if isinstance(x, DictObject):
            s+= x.__str__(indent+2)
          else:
            s+="%s" % val
          s+="\n"
        s+= " " * indent
        s+="]\n" 
      else:
        s+=" " * indent
        s+="%s = \"%s\"\n" % (key, val)
    indent-=2
    s+=" " * indent
    s+="}\n"
    return s

