##############################################################################
#
#     generator.py
#     Copyright (c) 2018 Raphael DINGE
#
#Tab=3########################################################################

import logging
import os
import sys
from .ast import Design, Component, Fiducial, Rect, Point


class Generator (object):

   def __init__ (self, manufacturer):
      self._manufacturer = manufacturer


   #-- process_bom -------------------------------------------------------------------

   def process_bom (self, output_path, design):
      if self._manufacturer == 'pcbpool':
         self._process_bom_pcbpool (output_path, design)
      else:
         logging.error ("\033[91mfatal error:\033[0m Unknown manufacturer `%s'", self._manufacturer)
         sys.exit (1)



   #-- _process_pcbpool_bom ----------------------------------------------------------

   def _process_bom_pcbpool (self, output_path, design):
      with open (os.path.join (output_path, '%s.bom.csv' % design.name), 'w') as output:
         output.write ('Part;Value;Device;Package;Description;Description2;Quantity;Place;Provided;Distributor;Distributor Part Number;Distributor Link;Remarks;Unit Price;Total Price;Remarks Beta;Option1;Option2;Option3\n')

         for description in design.descriptions:
            quantity = 0
            refs = []
            curcomp = None
            for reference in design.references:
               component = design.components [reference]
               if component.description == description:
                  curcomp = component
                  quantity += 1
                  refs.append (component.reference)
            value = curcomp.value
            if curcomp.reference.startswith ('J'):
               value = ""
            output.write (
               '%s;%s;%s;%s;%s;;%s;%s;No;%s;%s;%s;%s;;;;;;\n' %
               (', '.join (refs), value,
               curcomp.device, curcomp.package,
               curcomp.description, quantity, curcomp.place,
               curcomp.distributor, curcomp.distributor_part_number, curcomp.distributor_link,
               curcomp.remark)
            )



   #-- process_pickplace -------------------------------------------------------------

   def process_pickplace (self, output_path, design):
      if self._manufacturer == 'pcbpool':
         self._process_pickplace_pcbpool (output_path, design)
      else:
         logging.error ("\033[91mfatal error:\033[0m Unknown manufacturer `%s'", self._manufacturer)
         sys.exit (1)



   #-- _process_pcbpool_pickplace ----------------------------------------------------

   def _process_pickplace_pcbpool (self, output_path, design):
      with open (os.path.join (output_path, '%s.pickplace.txt' % design.name), 'w') as output:
         output.write ('Filename:\t%s.pickplace.txt\n\n' % design.name)
         output.write ('Position of PCB:\nleft under edge: X=0 / Y=0\n\n\n')
         output.write ('name\tX-axis\tY-axis\tangle\tvalue\tpackage\tside\n\n')

         def to_position_x (design, x):
            return x - design.outline.left

         def to_position_y (design, y):
            return design.outline.bottom - y

         for fiducial in design.fiducials:
            output.write (
               '%s\t%.2f\t%.2f\t0.00\t1mm\tCircle\t%s\n' %
               (fiducial.reference,
               to_position_x (design, fiducial.position.x), to_position_y (design, fiducial.position.y),
               fiducial.side)
            )

         output.write ('\n')

         for key, component in design.components.items ():
            output.write (
               '%s\t%.2f\t%.2f\t%.2f\t%s\t%s\t%s\n' %
               (component.reference,
               to_position_x (design, component.position.x),
               to_position_y (design, component.position.y),
               component.rotation,
               component.value, component.package, component.side)
            )

