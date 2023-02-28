
rem Transparent pixels in images should not update Z-buffer
git apply ..\merryoncherry\MoCbuild\gl.diff

rem Arches that zigzag

rem Issue when starting without .xcontroller files
git apply ..\merryoncherry\MoCbuild\ctrl.diff

rem Disable dark mode
git apply ..\merryoncherry\MoCbuild\dark.diff

rem Ripple rotation value curve not working
git apply ..\merryoncherry\MoCbuild\ripple.diff

rem Don't warn about old FPP
git apply ..\merryoncherry\MoCbuild\nowarn.diff

rem Set version to moc
git apply ..\merryoncherry\MoCbuild\version.diff
