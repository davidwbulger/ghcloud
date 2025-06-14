##  CONVERT A SIMPLY FORMATTED SONGBOOK TO EPUB FORMAT  #######################

#==============================================================================
##  PREAMBLE  #################################################################
#==============================================================================

from datetime import datetime
import html
from itertools import chain
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

##  COMMAND-LINE ARGUMENTS  ###################################################
# Allowable syntaxes should include
#   python makeSongBook.py  #  take input from source.txt, output songbook.epub
#   python makeSongBook.py source.txt  #  same
#   python makeSongBook.py source.txt songbook  #  same
#   python makeSongBook.py source.txt songbook true  #  same but don't tidy up
if (len(sys.argv) > 4):
  raise ValueError(
    f"Usage: python {sys.argv[0]} sourcefile targetfile")
sourcefile = "source.txt" if len(sys.argv) < 2 else sys.argv[1]
targetfile = "songbook" if len(sys.argv) < 3 else sys.argv[2]
keepUnzipped = False if len(sys.argv) < 4 else (sys.argv[3][0].upper() in "TY")

# The following UUID is hard coded in content.opf because I'm at present just
# working on one, gradually growing document. I got it from
# www.uuidgenerator.net/version4: "e5a27505-8389-405f-823e-4569e30647c4"
# This is probably the dumbest thing I'm doing in this whole project.

##  SET UP THE FILES & FOLDERS  ###############################################
if not os.path.isfile(sourcefile):
  raise ValueError(
    f"Source file '{sourcefile}' not found.")

pzFolder = targetfile+"PreZip"
if os.path.exists(pzFolder):
  suf = 0  #  numerical suffix to uniquate output
  while os.path.exists(f"{pzFolder}{suf}"):
    suf += 1
  pzFolder = f"{pzFolder}{suf}"
  print(f"To avoid overwriting, temporary files will go to {pzFolder}.")

shutil.copytree('Template', pzFolder)

##  READ THE TEMPLATE FOR INDIVIDUAL SONGS  ###################################
with open("songTemplate.html") as fid:
  stemp = fid.read()

##  ALSO READ THE TEMPLATE FOR THE SELF-CONTAINED HTML VERSION  ###############
with open("schtmlTemplate.html") as fid:
  schtml = fid.read()
schtmlInnards = ""
  
##  CREATE AN EPUB OBJECT AND ADD THE COVER  ##################################
def dispatchSong(html, filenum):
  global schtmlInnards
  with open(os.path.join(pzFolder,'OEBPS',f'item{filenum}.xhtml'), 'w') as f:
    f.write(stemp.replace("[[SONG CONTENT]]", html))
  schtmlInnards += html

##  PROCESS THE SOURCE FILE  ##################################################
songnum = -1  #  0-indexed, so this means we aren't processing a song yet
titleList = []
with open(sourcefile) as source_fid:
  # Firstly, skip over any preamble:
  for line in source_fid:
    if re.match(r"\[title\]", line.strip(), re.IGNORECASE):
      break
  for line in chain([line], source_fid):

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
        case "title":
          if songnum >= 0:
            dispatchSong(innards, songnum+1)
          songnum += 1
          title = content.strip()
          titleList.append(title)
          print(f'Song number {songnum} has title "{title}"')
          innards = f"<h1>{title}</h1>\n"
        case "credit":
          innards += f"<h2>{content.strip()}</h2>\n"
        case "structure":
          innards += f"<p class='structure'>{content}</p>\n"
        case _:
          raise ValueError(
            f"Unknown command [{command}] in {sourcefile}.")
    elif line.strip() == "":
      innards += "<p class='br'></p>\n"
    else:
      csscl = 'lyric chords' if re.search(r'{.*}', line) else 'lyric'
      # This seems to be the problematic case, but not the solution:
      # if re.search(r'} *$',line):
      #   line += r'&nbsp;'
      lyric = re.sub(r'{([^}]*)}', r'<sup class="chord">\1</sup>', line)
      innards += f"<p class='{csscl}'>{lyric}</p>\n"

##  WRITE THE EPUB FILE  ######################################################
if songnum<0:
  raise ValueError(f"No songs found in source file '{sourcefile}'.")
else:
  dispatchSong(innards, songnum+1)  #  final song still needs to be written!
  print(f'Total song count = {songnum+1}.')

##  WRITE THE SELF-CONTAINED HTML VERSION  ####################################
with open('SongBook.html', 'w') as f:
  f.write(schtml.replace("[[SONG CONTENT]]", schtmlInnards))

##  UPDATE CONTENT.OPF  #######################################################
with open(os.path.join(pzFolder,'OEBPS','content.opf')) as fid:
  filetext = fid.read()
filetext = filetext.replace("[[ISODATE]]", datetime.now().strftime("%Y-%m-%d"))
filetext = filetext.replace("[[MANIFEST LIST]]", '\n'.join(['    ' +
  f'<item href="item{n}.xhtml" id="item{n}" ' +
  'media-type="application/xhtml+xml"/>' for n in range(1,songnum+2)]))
filetext = filetext.replace("[[SPINE LIST]]", '\n'.join([
  f'    <itemref idref="item{n}"/>' for n in range(1,songnum+2)]))
with open(os.path.join(pzFolder,'OEBPS','content.opf'), 'w') as fid:
  fid.write(filetext)

##  UPDATE TOC.HTML  ##########################################################
with open(os.path.join(pzFolder,'OEBPS','toc.html')) as fid:
  filetext = fid.read()
filetext = filetext.replace("[[CHAPTER LIST]]", '\n'.join([
  f'    <p><a href="item{n+1}.xhtml">{title}</a></p>'
  for (n,title) in enumerate(titleList)]))
with open(os.path.join(pzFolder,'OEBPS','toc.html'), 'w') as fid:
  fid.write(filetext)

##  UPDATE TOC.NCX  ###########################################################
with open(os.path.join(pzFolder,'OEBPS','toc.ncx')) as fid:
  filetext = fid.read()
filetext = filetext.replace("[[NAVPOINT LIST]]", '\n'.join([
  f'    <navPoint id="item{n+1}" playOrder="{n+2}">\n' +
  f'      <navLabel><text>{title}</text></navLabel>\n' +
  f'      <content src="item{n+1}.xhtml"/>\n    </navPoint>'
  for (n,title) in enumerate(titleList)]))
with open(os.path.join(pzFolder,'OEBPS','toc.ncx'), 'w') as fid:
  fid.write(filetext)

##  CREATE THE EPUB FILE  #####################################################

# Not doing it this way because we can't control file order:
# shutil.make_archive(targetfile+'.epub', 'zip', pzFolder)

epub = zipfile.ZipFile(targetfile+'.epub', 'w')
epub.writestr("mimetype", "application/epub+zip")

for (folder,_,fileList) in os.walk(pzFolder):
  folderWithinArchive = Path(folder).relative_to(pzFolder)
  for f in fileList:
    epub.write(os.path.join(folder, f), os.path.join(folderWithinArchive, f))

epub.close()
