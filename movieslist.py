#!/usr/bin/env python3

import sys
import os
from os.path import isdir, join


def getAllDirectoriesInPath(path):
  # get all dirs list without a dot in the beginning
  dirs = [d for d in os.listdir(join(".", path)) if isdir(join(path, d)) and not (d.startswith("."))]
  if len(dirs) == 0:
    print("No folders found")
    exit(0)

  return dirs.sort()

def main():
  # the root path for a directory tree search is given
  # in the args of the script. when ommitted, the root is "."
  if len(sys.argv) >= 2:
    path = sys.argv[1]
  else:
    path = "."

  dirs = getAllDirectoriesInPath(path)
  
  f = open("movies.txt", "w")
  for dir in dirs:
    f.write(dir + "\n")


  

if __name__ == '__main__':
  main()