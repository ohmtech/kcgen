##############################################################################
#
#     parser.py
#     Copyright (c) 2018 Raphael DINGE
#
#Tab=3########################################################################

from .ast import Design, Component, Fiducial, Rect, Point
from string import whitespace



class Parser (object):

   def __init__ (self, name, data_net, data_pcb):
      self._name = name
      self._data_net = data_net
      self._data_pcb = data_pcb
      self._atom_end = set ('()"\'') | set (whitespace)


   def parse (self):
      design = self._parse_design ()

      #print design

      return design



   #-- _parse_design --------------------------------------------------------------

   def _parse_design (self):
      design = Design ()
      design.name = self._name

      # read net file

      net_root = self._parse_sexpression (self._data_net)
      net_design = self._find_node (net_root, 'design')
      net_date = self._find_node (net_design, 'date')
      design.date = self._value (net_date)

      net_components = self._find_node (net_root, 'components')
      for c in range (1, len (net_components)):
         net_comp = net_components [c]
         component = Component ()

         net_ref = self._find_node (net_comp, 'ref')
         component.reference = self._value (net_ref)

         net_value = self._find_node (net_comp, 'value')
         component.value = self._value (net_value)

         net_fields = self._find_node (net_comp, 'fields')
         if net_fields != None:
            for f in range (1, len (net_fields)):
               net_field = net_fields [f]
               field_key = self._to_string (net_field [1][1])
               field_value = self._to_string (net_field [2])
               if field_key == 'Device':
                  component.device = field_value
               elif field_key == 'Package':
                  component.package = field_value
               elif field_key == 'Description':
                  component.description = field_value
               elif field_key == 'Place':
                  component.place = field_value.upper () == 'YES'
               elif field_key == 'Dist':
                  component.distributor = field_value
               elif field_key == 'DistPartNumber':
                  component.distributor_part_number = field_value
               elif field_key == 'DiskLink':
                  component.distributor_link = field_value
               elif field_key == 'Remark':
                  component.remark = field_value


         design.components [component.reference] = component
         design.descriptions.add (component.description)

      # read pcb file
      # order of modules follows naming natural order apparently

      pcb_root = self._parse_sexpression (self._data_pcb)

      fiducial_top_idx = 1
      fiducial_bottom_idx = 1

      outline_left = None
      outline_top = None
      outline_right = None
      outline_bottom = None

      for i in range (1, len (pcb_root)):
         pcb_element = pcb_root [i]
         if self._key (pcb_element) == 'module':
            pcb_module = pcb_element
            pcb_at = self._find_node (pcb_module, 'at')
            x = float (self._to_string (pcb_at [1]))
            y = float (self._to_string (pcb_at [2]))
            rot = 0
            if len (pcb_at) == 4:
               rot = float (self._to_string (pcb_at [3]))
            pcb_ref = self._find_node2 (pcb_module, 'fp_text', 'reference')
            reference = self._to_string (pcb_ref [2])
            layer = self._to_string (pcb_ref [4][1])

            if reference == 'REF**':
               fiducial = Fiducial ()
               if layer == 'F.SilkS':
                  fiducial.reference = 'REF%sT' % fiducial_top_idx
                  fiducial.side = 'top'
                  fiducial_top_idx += 1
               else:
                  fiducial.reference = 'REF%sB' % fiducial_bottom_idx
                  fiducial.side = 'bottom'
                  fiducial_bottom_idx += 1
               fiducial.position.x = x
               fiducial.position.y = y
               design.fiducials.append (fiducial)
            if reference == 'G***':
               pass # skip
            else:
               design.references.append (reference)
               component = design.find_component (reference)
               component.position.x = x
               component.position.y = y
               component.rotation = rot
               if layer == 'F.SilkS':
                  component.side = 'top'
               else:
                  component.side = 'bottom'
         elif self._key (pcb_element) == 'gr_line':
            pcb_line = pcb_element
            pcb_layer = self._find_node2 (pcb_line, 'layer', 'Edge.Cuts')
            if pcb_layer != None:
               pcb_start = self._find_node (pcb_line, 'start')
               pcb_end = self._find_node (pcb_line, 'end')
               start_x = float (self._to_string (pcb_start [1]))
               start_y = float (self._to_string (pcb_start [2]))
               end_x = float (self._to_string (pcb_end [1]))
               end_y = float (self._to_string (pcb_end [2]))
               if outline_left == None:
                  outline_left = start_x
               if outline_top == None:
                  outline_top = start_y
               if outline_right == None:
                  outline_right = start_x
               if outline_bottom == None:
                  outline_bottom = start_y
               outline_left = min (outline_left, start_x, end_x)
               outline_right = max (outline_right, start_x, end_x)
               outline_top = min (outline_top, start_y, end_y)
               outline_bottom = max (outline_bottom, start_y, end_y)

         design.outline.left = outline_left
         design.outline.top = outline_top
         design.outline.right = outline_right
         design.outline.bottom = outline_bottom

      return design



   #-- _to_string --------------------------------------------------------------

   def _to_string (self, data):
      if type (data) is tuple: return data [0]
      else: return data



   #-- _key --------------------------------------------------------------

   def _key (self, node):
      return self._to_string (node [0])



   #-- _value --------------------------------------------------------------

   def _value (self, node):
      return self._to_string (node [1])



   #-- _find_node --------------------------------------------------------------

   def _find_node (self, node, search_key):
      for c in range (1, len (node)):
         sub_node = node [c]
         key = self._to_string (sub_node [0])
         if key == search_key:
            return sub_node
      return None



   #-- _find_node2 --------------------------------------------------------------

   def _find_node2 (self, node, search_key, search_subkey):
      for c in range (1, len (node)):
         sub_node = node [c]
         if len (sub_node) < 2:
            continue
         key = self._to_string (sub_node [0])
         subkey = self._to_string (sub_node [1])
         if key == search_key and subkey == search_subkey:
            return sub_node
      return None



   #-- _parse_sexpression --------------------------------------------------------------

   def _parse_sexpression (self, sexpr):

      stack, i, length = [[]], 0, len (sexpr)

      while i < length:
         c = sexpr [i]

         reading = type (stack[-1])

         if reading == list:
            if c == '(': stack.append ([])
            elif c == ')': 
               stack[-2].append (stack.pop ())
               if stack[-1][0] == ('quote',): stack[-2].append (stack.pop ())
            elif c == '"': stack.append ('')
            elif c == "'": stack.append ([('quote',)])
            elif c in whitespace: pass
            else: stack.append ((c,))
         elif reading == str:
            if c == '"':
               stack[-2].append (stack.pop ())
               if stack[-1][0] == ('quote',): stack[-2].append (stack.pop ())
            elif c == '\\': 
               i += 1
               stack[-1] += sexpr[i]
            else: stack[-1] += c
         elif reading == tuple:
            if c in self._atom_end:
               atom = stack.pop ()
               stack[-1].append( atom)
               if stack[-1][0] == ('quote',): stack[-2].append (stack.pop ())
               continue
            else: stack[-1] = ((stack[-1][0] + c),)
         i += 1
      return stack.pop () [0]

