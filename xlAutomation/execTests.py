import subprocess


#subprocess.run([self.bin+"\\"+"xlDo.exe", "-c", cmd], capture_output=False)
if 0:
    subprocess.run('python fseqFile.py '
        " -s m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.xsq "
        " -x m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars "
        " -o m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc.tmp " # Not a good place to put it
        " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.fseq "
        , capture_output=False)

subprocess.run('python compareFseqCRCs.py '
    " -c -f -m"
    " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc "
    " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc.tmp "
    , capture_output=False)


