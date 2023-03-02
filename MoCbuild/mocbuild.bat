rem Arches don't that zigzag
git apply ..\merryoncherry\MoCbuild\arch_zigzag.diff

rem Issue when starting without .xcontroller files
git apply ..\merryoncherry\MoCbuild\ctrl.diff

rem Disable dark mode
git apply ..\merryoncherry\MoCbuild\dark.diff

rem Don't warn about old FPP
git apply ..\merryoncherry\MoCbuild\nowarn.diff

rem Submodel tools
git apply ..\merryoncherry\MoCbuild\submodeltools.diff

rem Set version to moc
git apply ..\merryoncherry\MoCbuild\version.diff
