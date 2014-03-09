#!/usr/bin/python

import sys
import array
import re

def to_mswav(sFilename):
        """
        We need to convert the file to WAVEFORMATX to satisfy Skype

        sFilename = File to write
        """
        p = re.compile('16kHz.wav')
        convertedFilename = p.sub('16kHz-ms.wav', sFilename)
        #print "...sFilename... " + convertedFilename

        # Open the file, and create a temp file
        pFileIn = open(sFilename, "rb")
        pFileOut = open(convertedFilename, "wb")
        pBuf = array.array('B')

        # Read the first 44 bytes and make our modificates
        pBuf.fromfile(pFileIn,0x24)

        pBuf[0x10] +=2
        pBuf[0x04] +=2

        pBuf.tofile(pFileOut)
        pFileOut.write(chr(0x00))
        pFileOut.write(chr(0x00))
        pFileOut.flush()

        # Read rest of file
        try:
            while 1:
                pBuf = array.array('B')
                pBuf.fromfile(pFileIn,10000)
                pBuf.tofile(pFileOut)
        except:
            pBuf.tofile(pFileOut)


        pFileIn.close()
        pFileOut.close()

        # Delete Input file
        #os.remove(sFilename)
        #os.rename(sFilename+"-convert",sFilename)

        # Done
        return convertedFilename

if __name__ == '__main__':
        print to_mswav(sys.argv[1])
        #print 'This program is being run by itself'
