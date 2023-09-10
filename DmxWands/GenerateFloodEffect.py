# The purpose of this is to generate a track of a single color that captures the essence of the scene.
#  This could be used for anything that needs "just one color", like a flood light.
#  However, the intended target is more "interesting".  It is the DMX wireless wands / bracelets / etc.,
#    which do need a color, but also can only take an update a few times a second, and you also
#    may not want to run the transmitter continuously in case it causes interference.
# So the basic operation of this program is:
#  Look at the primary color / secondary color in each frame - yes, it uses the fseq file for this
#   You can look at a few models or all of them
#  Get a sense of the overall energy of the frame - when this changes, it is a good time to trigger the color
# There are some fine-tuning technical parameters:
#   Input files:
#     This needs the .fseq file, rgb_effects, and networks; that's how we tell how to read the colors
#     The model to use, or all RGB models by default
#   Transmitter control:
#     Name of the transmitter to use in the sequence
#     How long to strobe the transmitter - .075-.1 seconds works well
#     Minimum time between strobes
#     Channel data for the strobe - Ch 1 control (default 85), Ch 2 group (default 0)
#     Time advance for the strobe - in case of delay between strobe and wand action
#     Time advance for the color change before strobe - in case of delay between color and wand strobe
#   Color control:
#     Use brightness or do not use brightness?
#     Use a timing track to trigger?
#     Use the secondary color also?

import argparse
import textwrap
import sys

sys.path.append('../merryoncherry')
import xlAutomation.fseqFile
import xlAutomation.xsqFile

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    M, m = max(r, g, b), min(r, g, b)
    C = M - m
    
    # Hue calculation
    if C == 0:
        H = 0
    elif M == r:
        H = (60 * ((g - b) / C) + 360) % 360
    elif M == g:
        H = (60 * ((b - r) / C) + 120) % 360
    elif M == b:
        H = (60 * ((r - g) / C) + 240) % 360

    # Saturation calculation
    if M == 0:
        S = 0
    else:
        S = C / M

    # Value calculation
    V = M

    return H, S, V

# TODO: This is a ridiculous amount of work
#x Read the input file
#x Read the layout to
#   establish target model
#   and color order
#   and reverse gamma
#  Read the .fseq file
#  Get the typical color from the frame - sample or all?
#   Do this as HSV buckets
#   Get a sense of popularity and brightness
#   Pick out the most popular and knock it out
#   Pick out the second most popular
#   Get a sense of overall significance energy level
#   Pick the times to do the changes
#   Make effects
#  Save
#  Test it

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=textwrap.dedent('''\
        xLights effect generator for floods/wands/bracelets/etc.
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--showdir', type=str, required = True, help='Directory with xlights_rgbeffects.xml and xlights_networks input file')
    parser.add_argument('--fseq', type=str, required = True, help='.fseq input file')
    parser.add_argument('--outxsq', type=str, required = True, help='Generated .xsq output')
    parser.add_argument('--modelsource', type=str, required = False, help = 'Source model(s) for RGB colors')
    parser.add_argument('--targetcontrol', type=str, default = 'DmxWandsCtrl', help = 'Target model for control pulses')
    parser.add_argument('--ch1val', type=int, default=85, help = 'Control Channel 1 (ID) value')
    parser.add_argument('--ch2val', type=int, default=0, help = 'Control Channel 2 (Group) value') 
    parser.add_argument('--targetcolor', type=str, default = 'DmxWands', help = 'Target model for colors')
    parser.add_argument('--controladvance', type=int, default=50, help = 'Milliseconds to advance the timing of the control strobe')
    parser.add_argument('--coloradvance', type=int, default=50, help = 'Milliseconds to advance the timing of the color')
    parser.add_argument('--controlwidth', type=int, default=75, help = 'Milliseconds to hold the control signal')
    parser.add_argument('--controlgap', type=int, default=50, help = 'Minimum milliseconds of gap to wait between control pulses')
    # TODO:
    parser.add_argument('--inxsq', type=str, required = False, help='Input .xsq, for timing track to trigger colors')
    parser.add_argument('--timingtrack', type=str, required = False, help = 'Timing track to use as a hint for sending color') # For this you need an input sequence...
    # TODO: Color control
    #parser.add_argument('--ncolors', type=int, default=1, help='Number of colors to extract and use')
    #Some tuning of how to handle the energy level?
    #Ramp up / down?

    args = parser.parse_args()

    controllers = []
    ctrlbyname = {}
    models = []
    smodels = []

    xlAutomation.fseqFile.readControllersAndModels(args.showdir, controllers, ctrlbyname, models, smodels)
    if args.inxsq:
        ttracks = []
        xlAutomation.xsqFile.readSequenceTimingTrack(args.inxsq, ttracks)


    numbers = [0] * 10000
