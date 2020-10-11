#!/usr/bin/env python

import os
import builtins as __builtin__
from PIL import Image, ImageOps  # ExifTags,

moduleList = {'osvmGlobals':'globs',
              'ExifDialog' :'ExifDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

#######            
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

# Rotate an image if needed
def rotateImage(filePath, exifData):
    rotation = {1:0, 3:180, 6:270, 8:90} # Required rotation in degrees

    if os.path.basename(filePath).split('.')[1].lower() != 'jpg':
        return

    try:
        orientation = exifData['Orientation']
    except:
        myprint('No \'Orientation\' tag found for file %s' % filePath)
        return

    if rotation[orientation]:
        newFilePath = os.path.join(globs.osvmDownloadDir,'%s-rot%d.%s' %
                                   (os.path.basename(filePath).split('.')[0],
                                    rotation[orientation],
                                    os.path.basename(filePath).split('.')[1]))
        if os.path.exists(newFilePath):
            return

        myprint('Rotating %s by %d degrees' % (filePath,rotation[orientation]))
        image = Image.open(filePath)
        exif = image.info['exif'] # Read exif from info attribute
        image = image.rotate(rotation[orientation], Image.NEAREST, expand=True)
        myprint('Creating: %s' % (newFilePath))
        image.save(newFilePath, exif=exif)
        #Create thumbnail of rotated image, keeping exif data
        size = (160,120)
        thumb = ImageOps.fit(Image.open(filePath).rotate(rotation[orientation], Image.ANTIALIAS, expand=True), size, Image.ANTIALIAS)
        thumb.save(os.path.join(globs.thumbDir,os.path.basename(newFilePath)),exif=exif)

        # Modify modification time
        os.utime(newFilePath, (0, os.path.getmtime(filePath)))

def main():
    globs.osvmDownloadDir = '/tmp'

    localFile = os.path.join(globs.osvmDownloadDir, 'P7032921.JPG')

    # Check if file needs rotation
    try:
        myprint('Checking if %s needs rotation' % os.path.basename(localFile))
        exifDataAsStr = exifDataDict[os.path.basename(localFile)]
    except:
        myprint('No Exif data for %s' % localFile)
    else:
        rotateImage.rotateImage(localFile, ast.literal_eval(exifDataAsStr))

    # Update Exif data cache file and re-load cache
    myprint('Updating Exif cache')
    exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
    if not os.path.exists(exifFilePath):
        myprint('%s does not exist. Creating' % exifFilePath)
        ExifDialog.saveExifDataFromImages(exifFilePath)
    else:   # Exif cache file already exists. Must update it
        try:
            myprint('Retrieving Exif Data for %s' % localFile)
            ed = ExifDialog.getExifData(localFile)
        except:
            myprint('Unable to get Exif data from file %s' % localFile)
        else:
            # Load existing exif data from file
            exifDataDict = ExifDialog.buildDictFromFile(exifFilePath)

            # Update dictionary containing exif data for all files
            myprint('Updating Exif Data Dict. Length=%d' % len(exifDataDict))
            try:
                foo = exifDataDict[os.path.basename(localFile)]
            except:
                myprint('exifDataDict[%s] does not exist. Adding.' % os.path.basename(localFile))
                exifDataDict[os.path.basename(localFile)] = str(ed)
            else:
                myprint('exifDataDict[%s] already exists.' % os.path.basename(localFile))

            # Update exif data cache file
            ExifDialog.saveFileFromDict(exifDataDict, exifFilePath)

    myprint('Updated Exif Data File. Reloading...')                    
    # Re-Load existing data from file after update
    exifDataDict = ExifDialog.buildDictFromFile(exifFilePath)

    #rotateImage.rotateImage(localFile, ast.literal_eval(exifDataAsStr))
    
if __name__ == "__main__":
    main()
        
