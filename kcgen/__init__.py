##############################################################################
#
#     __init__.py
#     Copyright (c) 2018 Raphael DINGE
#
#Tab=3########################################################################

from __future__ import print_function
import argparse
import fileinput
import logging
import os
import platform
import subprocess
import sys
from .parser import Parser
from .generator import Generator

if platform.system () == 'Darwin':
   sys.path.insert(0, "/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/")

elif platform.system () == 'Windows':
   sys.path.insert(0, "C:/Program Files/KiCad/lib/python2.7/site-packages/")

import pcbnew



PATH_THIS = os.path.abspath (os.path.dirname (__file__))



def parse_args ():
   arg_parser = argparse.ArgumentParser ()

   arg_parser.add_argument (
      '-q', '--quiet',
      dest = 'logging_level', default = logging.INFO,
      action = 'store_const', const = logging.ERROR,
      help = 'Provides less output.'
   )

   arg_parser.add_argument (
      '-v', '--verbose',
      dest = 'logging_level', default = logging.INFO,
      action = 'store_const', const = logging.DEBUG,
      help = 'Provides more output.'
   )

   arg_parser.add_argument (
      '--manufacturer',
      default = 'pcbpool',
      help = 'The manufacturer. Defaults to pcbpool.'
   )

   arg_parser.add_argument (
      '--input-net',
      help = 'The input net file.'
   )

   arg_parser.add_argument (
      '--input-pcb',
      help = 'The input kicad_pcb file.'
   )

   arg_parser.add_argument (
      '--output-dir',
      default = '.',
      help = 'The output directory. Defaults to current directory.'
   )

   return arg_parser.parse_args (sys.argv[1:])



def generate_pcb (args):
   check_args (args)
   generate_pcb_gerber (args)
   generate_pcb_drill (args)



def generate_pcb_gerber (args):
   logging.info ('Generating PCB gerber files')
   check_args (args)

   output_dir = os.path.join (args.output_dir, 'gerber')
   if not os.path.exists (output_dir):
      os.makedirs (output_dir)

   logging.info ('   Reading %s', args.input_pcb)

   board = pcbnew.LoadBoard (args.input_pcb)
   plot_controller = pcbnew.PLOT_CONTROLLER (board)

   plot_options = plot_controller.GetPlotOptions ()
   plot_options.SetOutputDirectory (output_dir)
   plot_options.SetPlotFrameRef (False)

   plot_options.SetLineWidth (pcbnew.FromMM (0.1))

   plot_options.SetAutoScale (False)
   plot_options.SetScale (1)
   plot_options.SetMirror (False)

   plot_options.SetUseGerberAttributes (True)
   plot_options.SetUseGerberProtelExtensions (True)

   plot_options.SetExcludeEdgeLayer (True)
   plot_options.SetUseAuxOrigin (False)
   plot_controller.SetColorMode (True)

   plot_options.SetSubtractMaskFromSilk (False)
   plot_options.SetPlotReference (True)
   plot_options.SetPlotValue (False)

   layers = [
      ("F.Cu", pcbnew.F_Cu, "Top layer"),
      ("B.Cu", pcbnew.B_Cu, "Bottom layer"),
      ("F.Paste", pcbnew.F_Paste, "Paste top"),
      ("B.Paste", pcbnew.B_Paste, "Paste bottom"),
      ("F.SilkS", pcbnew.F_SilkS, "Silk top"),
      ("B.SilkS", pcbnew.B_SilkS, "Silk top"),
      ("F.Mask", pcbnew.F_Mask, "Mask top"),
      ("B.Mask", pcbnew.B_Mask, "Mask bottom"),
      ("Edge.Cuts", pcbnew.Edge_Cuts, "Edges"),
   ]

   logging.info ('   Writing to %s' % output_dir)

   for layer_info in layers:
      plot_controller.SetLayer (layer_info[1])
      plot_controller.OpenPlotfile (layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
      plot_controller.PlotLayer ()

   plot_controller.ClosePlot()



def generate_pcb_drill (args):
   logging.info ('Generating PCB drill file')
   check_args (args)

   output_dir = os.path.join (args.output_dir, 'gerber')
   if not os.path.exists (output_dir):
      os.makedirs (output_dir)

   logging.info ('   Reading %s', args.input_pcb)

   board = pcbnew.LoadBoard (args.input_pcb)
   excellon_writer = pcbnew.EXCELLON_WRITER (board)

   excellon_writer.SetMapFileFormat (pcbnew.PLOT_FORMAT_GERBER)

   mirror = False
   minimal_header = False
   merge_pth_npth = True
   offset = pcbnew.wxPoint (0, 0)
   excellon_writer.SetOptions (mirror, minimal_header, offset, merge_pth_npth)

   metric_format = True
   excellon_writer.SetFormat (metric_format)

   generate_drill = True
   generate_map = False

   logging.info ('   Writing to %s' % output_dir)

   excellon_writer.CreateDrillandMapFilesSet (
      output_dir, generate_drill, generate_map
   )



def generate_bom (args):
   logging.info ('Generating BOM file')
   check_args (args)
   design = read_design (args.input_net, args.input_pcb)
   if not os.path.exists (args.output_dir):
      os.makedirs (args.output_dir)
   generator = Generator (args.manufacturer)
   logging.info ('   Writing to %s' % args.output_dir)
   generator.process_bom (args.output_dir, design)



def generate_pickplace (args):
   logging.info ('Generating Pick & Place file')
   check_args (args)
   design = read_design (args.input_net, args.input_pcb)
   if not os.path.exists (args.output_dir):
      os.makedirs (args.output_dir)
   generator = Generator (args.manufacturer)
   logging.info ('   Writing to %s' % args.output_dir)
   generator.process_pickplace (args.output_dir, design)



def generate_assembly_plan (args):
   logging.info ('Generating Assembly Plan file')
   check_args (args)

   logging.info ('   Reading %s', args.input_pcb)

   board = pcbnew.LoadBoard (args.input_pcb)
   plot_controller = pcbnew.PLOT_CONTROLLER (board)
   plot_options = plot_controller.GetPlotOptions ()
   plot_options.SetOutputDirectory (args.output_dir)
   plot_options.SetPlotFrameRef (False)
   plot_options.SetLineWidth (pcbnew.FromMM (0.1))

   plot_options.SetAutoScale (False)
   plot_options.SetScale (1)
   plot_options.SetMirror (False)

   plot_options.SetExcludeEdgeLayer (False)
   plot_options.SetUseAuxOrigin (False)
   plot_controller.SetColorMode (True)

   plot_options.SetSubtractMaskFromSilk (False)
   plot_options.SetPlotReference (True)
   plot_options.SetPlotValue (False)

   logging.info ('   Writing to %s' % args.output_dir)

   plot_controller.SetLayer (pcbnew.F_Fab)
   plot_controller.OpenPlotfile ("F_Fab", pcbnew.PLOT_FORMAT_SVG, "Fab top")
   file_svg = plot_controller.GetPlotFileName ()
   plot_controller.PlotLayer ()
   plot_controller.ClosePlot()

   modules = board.GetModules ()

   for line in fileinput.input (file_svg, inplace = 1):
      if '</svg>' in line:
         print ('<g style="fill:#000000; fill-opacity:0.0; stroke:#ff0000; stroke-width:30; stroke-opacity:1; stroke-linecap:round; stroke-linejoin:round;">')
         for module in modules:
            position = module.GetPosition ()
            print ('<path d="M%d %d L%d %d" />' % (position.x / 2540.0 - 100, position.y / 2540.0, position.x / 2540.0 + 100, position.y / 2540.0))
            print ('<path d="M%d %d L%d %d" />' % (position.x / 2540.0, position.y / 2540.0 - 100, position.x / 2540.0, position.y / 2540.0 + 100))
         print ('</g>')
      print (line, end = '')

   project_name = os.path.basename (os.path.normpath (os.path.dirname (os.path.abspath (args.input_pcb))))

   subprocess.check_call (
      ['/usr/local/bin/rsvg-convert',
      file_svg,
      '--format=pdf',
      '--output', os.path.join (args.output_dir, '%s.assembly.pdf' % project_name)],
      cwd = PATH_THIS
   )

   os.remove (file_svg)



def read_design (input_net, input_pcb):

   project_name = os.path.basename (os.path.normpath (os.path.dirname (os.path.abspath (input_pcb))))

   try:
      file_net = open (input_net, 'r')
   except IOError:
      logging.error ("\033[91mfatal error:\033[0m `%s' file not found", input_net)
      sys.exit (1)

   with file_net:
      logging.info ('   Reading %s', input_net)
      data_net = file_net.read ()

   try:
      file_pcb = open (input_pcb, 'r')
   except IOError:
      logging.error ("\033[91mfatal error:\033[0m `%s' file not found", input_pcb)
      sys.exit (1)

   with file_pcb:
      logging.info ('   Reading %s', input_pcb)
      data_pcb = file_pcb.read ()

   parser = Parser (project_name, data_net, data_pcb)
   design = parser.parse ()

   return design



def check_args (args):
   if args.input_net is None:
      logging.error ("\033[91mfatal error:\033[0m No input net file")
      sys.exit (1)

   if args.input_pcb is None:
      logging.error ("\033[91mfatal error:\033[0m No input pcb file")
      sys.exit (1)

   if args.manufacturer is None:
      logging.error ("\033[91mfatal error:\033[0m No manufacturer")
      sys.exit (1)

   if args.output_dir is None:
      logging.error ("\033[91mfatal error:\033[0m No output directory")
      sys.exit (1)



def main (args):

   if not hasattr (args, 'stream'):
      args.stream = sys.stdout
   logging.basicConfig (format = '%(message)s', level = args.logging_level, stream = args.stream)

   check_args (args)

   generate_pcb (args)
   generate_bom (args)
   generate_pickplace (args)
   generate_assembly_plan (args)



def script_main ():
   return main (parse_args ())



if __name__ == '__main__':
   sys.exit (script_main ())
