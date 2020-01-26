#!/usr/bin/env python3

import sys
import os
import re
import time

from os.path import isdir, isfile, join, splitext
from termcolor import colored

VIDEOQUALITY = ["480p", "720p", "1080p"]
FORMAT = ["BluRay", "Bluray", "Web-DL", "WEB-DL", "WebRip", "WEBRip", "AMZN", "NF", "WEB", "PROPER", "REPACK", "UNRATED", "REMASTERED", "UNCUT", "EXTENDED"]
ENCODING = ["X264", "x264", "h264", "H264", "h.264", "H.264", "x265", "X265", "H.265", "h.265", "AMZN", "DD5.1", "DD.5.1", "AAC", "DTS-HDC", "DDP5.1", "DD+5.1", "Atmos"]
VIDEOEXT = [".mp4", ".mkv"]
PUBLISHERS = ["-RARBG", "-FGT", "-DIMENSION", "-DRONES", "-FOCUS", "-SiGMA", "[rartv]", "[rarbg]", "-DEFLATE", "-JETIX", "-NTb", "-TiTANS", "-AJP69", "-NTG", "-PSYCHD", "-ROVERS"]


def getAllDirectoriesInPath(path):
  # get all dirs list without a dot in the beginning
  dirs = [d for d in os.listdir(path) if isdir(join(path, d)) and not (d.startswith("."))]
  if len(dirs) == 0:
    print("No folders found")
    exit(0)

  return dirs

# returns true if folder contains media content guessing by keywords in the folder name
# e.g. publishers, format, resolution
def isMediaFolder(folderName):
  return (matchesFilter(folderName, VIDEOQUALITY) == 1 or matchesFilter(folderName, ENCODING) == 1 or
    matchesFilter(folderName, FORMAT) == 1 or matchesFilter(folderName, PUBLISHERS) == 1)

# returns true if the folder contains tv show content and false otherwise
def isTVShow(name):
  match = re.match(r'.*(S[0-9]{2})', name)
  if match is not None:
    return True
  
  return False

# returns true if the given name has any matches with the filter arrays
def matchesFilter(name, filter):
  for entry in filter:
    if entry.lower() in name.lower(): return 1
  
  return 0

# generate beautiful name
def beautifulName(name):
  newName = name

  if os.path.isfile(join('.', name)):
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
    # lower case test
    if enc.lower() in newName.lower():
      newName = newName.replace(enc.lower(), "")

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

  # lastly, remove all the dots and replace them with spaces
  newName = re.sub("\.+", " ", newName)
  
  return newName.strip()

def organiseTVShow(folderName):
  show = beautifulName(folderName)
  season = ""

  # get season number
  match = re.match(r'.*(S[0-9]{2})', show)
  if match is not None:
    season = 'Season ' + str(int(match.group(1)[1:]))
    show = show.replace(match.group(1), "").strip()

  print('Organising TV show', colored(show, 'red'), colored(season, 'red'), end="")

  # create tv show's folder if it doesn't exist
  if not os.path.isdir(show):
    os.rename(folderName, show)
  
  # go to tv show's folder
  os.chdir(show)

  # create season folder if it doesn't exist
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
      if not epTitle.startswith('-') and len(epTitle) > 0:
        renamed = renamed[:renamed.index(epTitle)] + "- " + epTitle      

      # rename video file  
      os.rename(f, renamed + filext)

      # create episode folder under season folder
      # if it doesn't exist and move file to it
      if len(epTitle) > 0:
        epFolder = join(".", season, renamed[:renamed.index(match.group(1))+6])
      else:
        epFolder = join(".", season, renamed)

      if not os.path.exists(epFolder) or not os.path.isdir(epFolder):
        os.mkdir(epFolder)
        os.rename(renamed + filext, join(epFolder, renamed + filext))

  os.chdir('..')
  
  return show

def organiseMovie(folderName):
  originalName = folderName
  movie = beautifulName(folderName)

  print('Organising movie', colored(movie, 'red'), end="")

  # rename movie folder to the new name
  os.rename(folderName, movie)

  os.chdir(movie)

  # filter every file in the directory
  for f in os.listdir("."):
    # get the extension to decide what to do with it
    _, fileext = splitext(f)

    # remove all .txt files currently residing 
    if fileext.lower() == ".txt" or fileext.lower() == ".exe":
      os.remove(f)

    # ignore subs folder
    if isdir(f) and f == "Subs":
      continue

    # find video file to rename it with the new beautiful
    for ext in VIDEOEXT:
      if fileext.lower() in ext.lower():
        os.rename(f, movie + fileext.lower())


  # include original folder name in case it is useful in the future
  with open("info.txt", "w+") as infoFile:
    infoFile.write(originalName)

  # go back to the root folder
  os.chdir('..')

  return movie


# script initiates here
def main():
  # initialisation
  # enable console colors
  os.system('color')
  
  showsOrganised = []
  moviesOrganised = []

  # the root path for a directory tree search is given
  # in the args of the script. when ommitted, the root is "."
  if len(sys.argv) > 2:
    path = sys.argv[1]
  else:
    path = "."

  # get all dirs list without a dot in the beginning
  dirs = list( dir for dir in getAllDirectoriesInPath(path) if isMediaFolder(dir) == True )
  print("Entertainment directories found:", colored(len(dirs), "green" if len(dirs) > 0 else "red"))

  timeStart = round(float(time.time()), 2)
  # filter all dirs and try to guess if the folder contains
  # entertainment content
  for d in dirs:
    # detect if this is a movie or tv show folder
    
    itemTimerStart = round(float(time.time()), 2)
    if isTVShow(d):
      showsOrganised.append(organiseTVShow(d))
    else:
      moviesOrganised.append(organiseMovie(d))
    itemTimeElapsed = round(float(time.time()) - itemTimerStart, 2)
    print(" (" + colored(str(itemTimeElapsed) + "s", "green") + ")")
  
  timeElapsed = round(float(time.time()) - timeStart, 2)

  # exit if there are no directories with content
  if len(dirs) > 0:
    print("\n\n")
    print("TV shows organised:", len(showsOrganised))
    print("Movies organised:", len(moviesOrganised))
    print("Took", colored(timeElapsed, "green"), "seconds.")
  else:
    exit(0)


if __name__ == '__main__':
    main()