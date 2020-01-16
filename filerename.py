#!/usr/bin/env python3

import sys
import os
import re

from os.path import isdir, isfile, join, splitext

VIDEOQUALITY = ["480p", "720p", "1080p"]
FORMAT = ["BluRay", "Bluray", "Web-DL", "WebRip", "WEBRip"]
ENCODING = ["X264", "x264", "h264", "H264", "x265", "X265", "AMZN", "DD5.1", "AAC"]
VIDEOEXT = [".mp4", ".mkv"]
PUBLISHERS = ["-RARBG", "-FGT", "-DIMENSION", "-DRONES", "-SiGMA", "[rartv]", "[rarbg]"]

# guess if the folder contains entertainment content
def guessByFilter(name, filter):
  for entry in filter:
    if entry.lower() in name.lower(): return 1
  
  return 0

# generate beautiful name
def beautifullyName(name):
  newName = name.replace(".", " ")

  # remove video quality
  for quality in VIDEOQUALITY:
    if quality in newName:
      newName = newName.replace(quality, "")
  
  # remove video format
  for videoFormat in FORMAT:
    if videoFormat.lower() in newName.lower():
      newName = newName.replace(videoFormat.lower(), "")
      newName = newName.replace(videoFormat, "")

  # remove audio quality
  for enc in ENCODING:
    if enc in newName:
      newName = newName.replace(enc, "")

  # remove publishers
  for pub in PUBLISHERS:
    if pub in newName:
      newName = newName.replace(pub, "")
  

  # remove year of release
  match = re.match(r'.*([1-3][0-9]{3})', newName)
  if match is not None:
    # if there is a match, it's highly likely it's the year of release
    # and not anything else related to the entertainment
    # but even if it is, we just want the title
    newName = newName.replace(match.group(1), "")

  return newName.strip()

def main():
  nameDirs = []

  if len(sys.argv) > 2:
    path = sys.argv[1]
  else:
    path = "."

  # get all dirs list without a dot in the beginning
  dirs = [d for d in os.listdir(path) if isdir(join(path, d)) and not (d.startswith("."))]
  if len(dirs) == 0:
    print("No folders found")
    exit(0)

  dirsCount = 0
  # filter all dirs and try to guess if the folder contains
  # entertainment content
  for d in dirs:
    # guess video quality
    if (guessByFilter(d, VIDEOQUALITY) == 1 or guessByFilter(d, ENCODING) == 1 or
      guessByFilter(d, FORMAT) == 1 or guessByFilter(d, PUBLISHERS) == 1):
      dirsCount += 1

      newName = beautifullyName(d)
      os.rename(d, newName)
      
      nameDirs.append(newName)
    else: 
      dirs.pop(dirs.index(d))

  print("Entertainment directories found: ", dirsCount)

  # exit if there are no directories with content
  if dirsCount == 0:
    exit(1)

  # rename video files under directories
  for d in nameDirs:
    # change directory to the entertainment directory
    os.chdir(join(os.getcwd(), d))

    for f in os.listdir("."):
      _, fileext = splitext(f)

      # remove all .txt files included in downloads
      if fileext.lower() == ".txt":
        os.remove(f)

      # find video file to rename it
      for ext in VIDEOEXT:
        if fileext.lower() in ext.lower():
          os.rename(f, d + fileext.lower())

    # include original folder name in case it is useful in the future
    with open("info.txt", "w+") as infoFile:
      infoFile.write(dirs[nameDirs.index(d)])

    # go back to the root folder
    os.chdir("../")


if __name__ == '__main__':
    main()