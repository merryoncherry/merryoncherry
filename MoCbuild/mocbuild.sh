:
# Label size in grids
echo "Label size in grids"
git apply ../merryoncherry/MoCbuild/labelsize.diff

# Set version to moc
echo "Set Version"
git apply ../merryoncherry/MoCbuild/version.diff

# Add descriptions
echo "Descriptions"
git apply ../merryoncherry/MoCbuild/descriptions.diff

# Preview vid CLI
echo "Preview vid"
git apply ../merryoncherry/MoCbuild/previewvid.diff
