# kcgen

Automatic PCB production files generation from KiCad schematics, net and routing files


## Requirements

- [KiCad 5.0 for MacOS X](http://kicad-pcb.org/download/osx/) or higher (in particular, KiCad 4 won't work properly)
- `rsvg-convert` in `/usr/local/bin/`

## Installing RSVG

```
brew install librsvg
```

## Usage from Python

The python embedded in KiCad must be used (see shebang on first line below),
it is assumed in the following that KiCad is installed at its default location `/Applications/KiCad/`

```
#!/Applications/KiCad/kicad.app/Contents/Frameworks/Python.framework/Versions/2.7/bin/python2.7

import kcgen

# Create an empty python object
args = lambda: None

# Set the path to the net file generated from the schematics
args.input_net = 'myproject.net'

# Set the path to the routing file
args.input_pcb = 'myproject.kicad_pcb'

# Set the target manufacturer. For now only PCB Pool is supported
args.manufacturer = 'pcbpool'

# Set the output dir to generate the files
args.output_dir = 'output'

# Generate the gerber files for PCB production
kcgen.generate_pcb (args)

# Generate the BOM for component ordering (see section below)
kcgen.generate_bom (args)

# Generate pick & place file for PCBA manufacturing
kcgen.generate_pickplace (args)

# Generate assembly plan file for PCBA manufacturing or private usage
kcgen.generate_assembly_plan (args)
```

## Usage from the shell

```
$ ./kcgen.py --help
usage: kcgen.py [-h] [-q] [-v] [--manufacturer MANUFACTURER]
                [--input-net INPUT_NET] [--input-pcb INPUT_PCB]
                [--output-dir OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Provides less output.
  -v, --verbose         Provides more output.
  --manufacturer MANUFACTURER
                        The manufacturer. Defaults to pcbpool.
  --input-net INPUT_NET
                        The input net file.
  --input-pcb INPUT_PCB
                        The input kicad_pcb file.
  --output-dir OUTPUT_DIR
                        The output directory. Defaults to current directory.
```

## Schematic file requirements

It is expected that at the schematic stage that the user will fill in some field in the component
properties. Those fields are:

- `Device`: The category of the component, for example "Fully differential Amplifier"
- `Package`: The canonical name of the package, for example "8-SOIC"
- `Description`: The description as copied from your distributor, for example "IC OPAMP AUDIO 180MHZ 8SOIC"
- `Place`: `Yes` or `No`, indicated to the PCBA manufacturer if the component should be placed by the pick & place machine
- `Dist`: The distributor, for example "DigiKey"
- `DistPartNumber`: The part number, in the distributor referential (ie. **not** the manufacturer part number), for example 296-16679-5-ND
- `DistLink`: The URL to the distributor component URL, for example https://www.digikey.com/product-detail/en/texas-instruments/OPA1632D/296-16679-5-ND/611295





