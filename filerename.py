#!/usr/bin/env python3

import sys
import os
import re

from os.path import isdir, isfile, join, splitext

VIDEOQUALITY = ["480p", "720p", "1080p"]
FORMAT = ["BluRay", "Bluray", "Web-DL", "WEB-DL", "WebRip", "WEBRip", "AMZN", "NF", "WEB"]
ENCODING = ["X264", "x264", "h264", "H264", "h.264", "H.264" "x265", "X265", "H.265", "h.265""AMZN", "DD5.1", "DD.5.1", "AAC", "DTS-HDC", "DDP5.1"]
VIDEOEXT = [".mp4", ".mkv"]
PUBLISHERS = ["-RARBG", "-FGT", "-DIMENSION", "-DRONES", "-FOCUS", "-SiGMA", "[rartv]", "[rarbg]", "-DEFLATE"]


def getAllDirectoriesInPath(path):
  # get all dirs list without a dot in the beginning
  dirs = [d for d in os.listdir(path) if isdir(join(path, d)) and not (d.startswith("."))]
  if len(dirs) == 0:
    print("No folders found")
    exit(0)

  return dirs

# guess if the folder contains entertainment content
def guessByFilter(name, filter):
  for entry in filter:
    if entry.lower() in name.lower(): return 1
  
  return 0

# generate beautiful name
def beautifulName(name):
  newName = name

  if os.path.isfile(join(".", name)):
    filename, _ = splitext(join(".", name))
    newName = filename

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
    if enc.lower() in newName.lower():
      newName = newName.replace(enc.lower(), "")
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

  # lastly, remove all the dots and replace them with spaces
  newName = newName.replace(".", " ")
  
  return newName.strip()

def seriesFolderOrganisation(folderName):
  show = beautifulName(folderName)

  # get season number
  match = re.match(r'.*(S[0-9]{2})', show)
  if match is not None:
    season = "Season " + str(int(match.group(1)[1:]))
    show = show.replace(match.group(1), "")

  # create series folder and enter it
  if not os.path.isdir(show):
    os.rename(folderName, show)
  
  # go to show folder
  os.chdir(show)

  # create season folder
  if not os.path.exists(season):
    os.mkdir(season)

  for f in os.listdir("."):
    # ignore folders
    if isdir(f):
      continue

    # get file information
    filename, filext = splitext(f)

    # delete all txt files and ignore all non-video ones
    if filext.lower() == ".txt":
      os.remove(f)
    elif filext not in VIDEOEXT:
      continue

    # get season and episode number
    # move file to the newly created episode folder
    renamed = beautifulName(filename)
    epTitle = ""
    
    match = re.match(r'.*(S[0-9]{2}E[0-9]{2})', renamed)
    if match is not None:
      epTitle = renamed[renamed.index(match.group(1))+7:]

      # add dash between episode and title if it's not there yet
      titlePosition = renamed.index(epTitle)
      if not epTitle.startswith('-') and len(epTitle) > 0:
        renamed = renamed[:titlePosition] + "- " + epTitle      
      os.rename(f, renamed + filext)

      # create episode folder under season folder
      # if it doesn't exist and move file to it
      if len(epTitle) > 0:
        epFolder = join(".", season, renamed[:renamed.index(match.group(1))+5])
      else:
        epFolder = join(".", season, renamed)


      if not os.path.exists(epFolder) or not os.path.isdir(epFolder):
        os.mkdir(epFolder)
      os.rename(renamed + filext,
        join(epFolder, renamed + filext))

  os.chdir('..')  

def main():
  if len(sys.argv) > 2:
    path = sys.argv[1]
  else:
    path = "."

  # get all dirs list without a dot in the beginning
  dirs = getAllDirectoriesInPath(path)

  dirsCount = 0
  # filter all dirs and try to guess if the folder contains
  # entertainment content
  for d in dirs:
    # guess video quality
    if (guessByFilter(d, VIDEOQUALITY) == 1 or guessByFilter(d, ENCODING) == 1 or
      guessByFilter(d, FORMAT) == 1 or guessByFilter(d, PUBLISHERS) == 1):
      dirsCount += 1

      # detect if this is a movie or tv show folder
      match = re.match(r'.*(S[0-9]{2})', d)
      if match is not None:
        seriesFolderOrganisation(d)
      else: 
        newFolderName = beautifulName(d)
        os.rename(d, newFolderName)

        # enter movie folder
        os.chdir(newFolderName)

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
            infoFile.write(dirs[d])

          # go back to the root folder
          os.chdir("../")
    else: 
      dirs.pop(dirs.index(d))

  print("Entertainment directories found:", dirsCount)

  # exit if there are no directories with content
  if dirsCount == 0:
    exit(1)    


if __name__ == '__main__':
    main()