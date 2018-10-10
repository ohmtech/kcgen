##############################################################################
#
#     ast.py
#     Copyright (c) 2018 Raphael DINGE
#
#Tab=3########################################################################

#pylint: disable=too-many-instance-attributes


class Point (object):
   def __init__ (self):
      self.x = 0.0
      self.y = 0.0

   def __str__ (self):
      return 'x: %s y: %s' % (self.x, self.y)


class Rect (object):
   def __init__ (self):
      self.left = 0.0
      self.right = 0.0
      self.top = 0.0
      self.bottom = 0.0

   def __str__ (self):
      return 'left:%s top: %s right: %s bottom: %s' % (self.left, self.top, self.right, self.bottom)



class Design (object):
   def __init__ (self):
      self.name = ""
      self.date = ""
      self.outline = Rect ()
      self.components = {}
      self.fiducials = []
      self.references = []
      self.descriptions = set ()

   def __str__ (self):
      ret =  'name: %s\n' % self.name
      ret += 'date: %s\n' % self.date
      ret += 'outline: %s\n' % self.outline
      ret += 'components:\n'
      for key, component in self.components.iteritems ():
         ret += '%s\n' % component
      ret += 'fiducials:\n'
      for fiducial in self.fiducials:
         ret += '%s\n' % fiducial
      ret += 'references: %s\n' % self.references
      ret += 'descriptions: %s' % self.descriptions
      return ret

   def find_component (self, reference):
      for key, component in self.components.iteritems ():
         if key == reference:
            return component
      return None


class Component (object):
   def __init__ (self):
      self.reference = ""
      self.value = ""
      self.position = Point ()
      self.rotation = 0.0
      self.side = ""
      self.device = ""
      self.package = ""
      self.description = ""
      self.place = True
      self.distributor = ""
      self.distributor_part_number = ""
      self.distributor_link = ""
      self.remark = ""

   def __str__ (self):
      ret =  '   %s: {\n' % self.reference
      ret += '      value: %s\n' % self.value
      ret += '      position: %s\n' % self.position
      ret += '      rotation: %s\n' % self.rotation
      ret += '      side: %s\n' % self.side
      ret += '      device: %s\n' % self.device
      ret += '      package: %s\n' % self.package
      ret += '      description: %s\n' % self.description
      ret += '      place: %s\n' % self.place
      ret += '      distributor: %s\n' % self.distributor
      ret += '      distributor_part_number: %s\n' % self.distributor_part_number
      ret += '      distributor_link: %s\n' % self.distributor_link
      ret += '      remark: %s\n' % self.remark
      ret += '   }'
      return ret



class Fiducial (object):
   def __init__ (self):
      self.reference = ""
      self.position = Point ()
      self.side = ""

   def __str__ (self):
      ret =  '   %s: {\n' % self.reference
      ret += '      position: %s\n' % self.position
      ret += '      side: %s\n' % self.side
      ret += '   }'
      return ret
