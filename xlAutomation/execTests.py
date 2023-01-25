import subprocess


#subprocess.run([self.bin+"\\"+"xlDo.exe", "-c", cmd], capture_output=False)
subprocess.run('python fseqFile.py '
    " -s m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.xsq "
    " -x m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars "
    " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.fseq ", capture_output=False)
