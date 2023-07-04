rem Arches don't that zigzag
git apply ..\merryoncherry\MoCbuild\arch_zigzag.diff

rem Don't warn about old FPP
git apply ..\merryoncherry\MoCbuild\nowarn.diff

rem Label size in grids
git apply ..\merryoncherry\MoCbuild\labelsize.diff

rem Set version to moc
git apply ..\merryoncherry\MoCbuild\version.diff
