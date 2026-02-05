##  CONVERT A SIMPLY FORMATTED SONGBOOK TO HTML FORMAT  #######################

#==============================================================================
##  PREAMBLE  #################################################################
#==============================================================================

import os
import re
import sys

##  COMMAND-LINE ARGUMENTS  ###################################################
# Allowable syntaxes should include
#   python makeSongBook.py  #  take input from source.txt, output songbook.html
#   python makeSongBook.py source.txt  #  same
#   python makeSongBook.py source.txt songbook  #  same
if (len(sys.argv) > 3):
  raise ValueError(
    f"Usage: python {sys.argv[0]} sourcefile targetfile")
sourcefile = "source.txt" if len(sys.argv) < 2 else sys.argv[1]
targetfile = "songbook" if len(sys.argv) < 3 else sys.argv[2]

##  SET UP THE FILES & FOLDERS  ###############################################
if not os.path.isfile(sourcefile):
  raise ValueError(
    f"Source file '{sourcefile}' not found.")

##  ALSO READ THE TEMPLATE FOR THE SELF-CONTAINED HTML VERSION  #############
with open("schtmlTemplate.html", encoding="utf-8") as fid:
  schtml = fid.read()
schtmlInnards = ""
title = ""
innards = ""

songDict = {}

def dispatchSong(html, title):
  # global schtmlInnards
  # schtmlInnards += html
  songDict[title] = html

def flushSong():
  if mode == "songdefs" and songnum >= 0:
    dispatchSong(innards, title)

##  PROCESS THE SOURCE FILE  ##################################################

# NECESSARY?
songnum = -1  #  0-indexed, so this means we aren't processing a song yet
titleList = []

with open(sourcefile, 'r', encoding='utf-8') as source_fid:
  mode = "preamble"

  for line in source_fid:

    # Want to use ampersands. Apparently html.escape converts only &,<,>. Let's
    # convert only ampersands, so we can still use <i> et cetera:
    # line = html.escape(line)
    line = re.sub('&', '&amp;', line)

    m = re.match(r"\[([^\]]*)\](.*)", line.strip())
    if m:
      (command,content) = m.groups()
      command = command.lower()
      match command:
        case "comment":
          pass
        case "layout":
          flushSong()
          mode = "layout"
        case "songdefs":
          mode = "songdefs"
        case "chapter":
          if mode != "layout":
            raise ValueError("[chapter] tag used out of layout mode")
          schtmlInnards += f"<h1>{content.strip()}</h1>\n"
        case "title":
          if mode != "songdefs":
            raise ValueError("[title] tag used out of songdefs mode")
          if songnum >= 0:
            dispatchSong(innards, title)
          songnum += 1
          title = content.strip()
          titleList.append(title)
          print(f'Song number {songnum} has title "{title}"')
          innards = f"<h2>{title}</h2>\n"
        case "credit":
          if mode != "songdefs":
            raise ValueError("[credit] tag used out of songdefs mode")
          innards += f"<h3>{content.strip()}</h3>\n"
        case "structure":
          if mode != "songdefs":
            raise ValueError("[structure] tag used out of songdefs mode")
          innards += f"<p class='structure'>{content}</p>\n"
        case _:
          raise ValueError(
            f"Unknown command [{command}] in {sourcefile}.")
    elif mode == "layout" and (titleref:=line.strip()) != "":
      schtmlInnards += f"[[SONG BY TITLE {titleref}]]\n"
    elif mode == "songdefs":
      if line.strip() == "":
        innards += "<p class='br'></p>\n"
      else:
        csscl = 'lyric chords' if re.search(r'{.*}', line) else 'lyric'
        lyric = re.sub(r'{([^}]*)}', r'<sup class="chord">\1</sup>', line)
        innards += f"<p class='{csscl}'>{lyric}</p>\n"

##  ADD THE LAST SONG TO THE DICT  ############################################
flushSong()

##  LOOK UP REFERENCED SONGS IN THE DICT  #####################################
pattern = re.compile(r"\[\[SONG BY TITLE ([^\]]+)\]\]")

def replace_lookup(match):
  title = match.group(1)
  try:
    return songDict[title]
  except KeyError:
    raise ValueError(f'Song not found by name "{title}"')

schtmlInnards = pattern.sub(replace_lookup, schtmlInnards)

##  WRITE THE SELF-CONTAINED HTML VERSION  ####################################
with open('SongBook.html', 'w', encoding="utf-8") as f:
  f.write(schtml.replace("[[SONG CONTENT]]", schtmlInnards))
