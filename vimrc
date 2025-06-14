set nu
set numberwidth=5  " including space between number & line
set ruler
set showcmd
set nojoinspaces
set shiftwidth=2
set noautoindent
set backspace=indent,start
set expandtab

set linebreak
set columns=79
set breakindent
set breakindentopt=shift:2

" SOME QUITE SPECIFIC COMMANDS:
command! GetSIDs :%s/.*\t\(\d\d\d\d\d\d\d\d\)\t.*/\1/ | g!/^\d\d\d\d\d\d\d\d$/d  "  USED IN SCRAPING HOMEWORK SUBMISSION DATA FROM iLEARN
command! Neufinder :exe 'g/Submitted for grading/-1j' | :%s/.*\t\(\d\d\d\d\d\d\d\d\)\t.*Submitted for grading.*/\1,1/ | exe 'g!/^\d\d\d\d\d\d\d\d,1$/d' | normal! 1GOSID,mark  "  USED IN SCRAPING HOMEWORK SUBMISSION DATA FROM iLEARN
command! NewWeek :normal! o72i*o========--------== DONE ==4k5yy4PjiM 5jiT 5jiW 5jiﬁ 5jiF 5j  "  ADDS A BLANK NEW WEEK TO A JOURNAL OR PLAN FILE

nnoremap <F3> :s/\(^.*$\)/<!-- \1 -->/<CR>
nnoremap <F4> 0gU$yy2pk:s/./=/g<CR>jj:s/./-/g<CR>  "  MAKE HEADING (CAPITALISE THE CURRENT LINE, UNDERLINE IT, AND DOUBLE-OVERLINE IT)
inoremap <F4> <esc>0gU$yy2pk:s/./=/g<CR>jj:s/./-/g<CR>o
" nnoremap <F7> 0gU$I##  <esc>A  <esc>73A#<esc>d79\|
nnoremap <F7> 0gU$I##  <esc>A  <esc>73A#<esc>079lD
inoremap <F8> <esc>Bhs<CR><esc>A

" HOMEBAKED LaTeX: PRESS F5 TO GET EITHER ERROR MESSAGES OR A PDF PREVIEW IN CHROME:
function! Pdflatexcurrentfile()
  if bufname("%") =~ ".tex$"
    update
    let texout=system("pdflatex -interaction=nonstopmode " . bufname("%"))
    if texout =~ "\n! "
      vsplit __pdflatex_error_messages__
      normal! 1GdG
      setlocal buftype=nofile
      call append(0, split(texout, '\v\n'))
    else
      let texout=system("pdflatex -interaction=nonstopmode " . bufname("%"))
      silent !start "C:\Program Files\Mozilla Firefox\firefox.exe" -new-window "%:p:r:s,$,.pdf,"
      "  silent !start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito "%:p:r:s,$,.pdf,"
      "  ! start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito "%:p:r:s,$,.pdf,"
      "  system("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito "%:p:r:s,$,.pdf,")
    endif
  else
    echo "Not a LaTeX file."
  endif
endfunction

nnoremap <F5> :call Pdflatexcurrentfile()<CR>

function! Lualatexcurrentfile()
  if bufname("%") =~ ".tex$"
    update
    let texout=system("lualatex -interaction=nonstopmode " . bufname("%"))
    if texout =~ "\n! "
      vsplit __pdflatex_error_messages__
      normal! 1GdG
      setlocal buftype=nofile
      call append(0, split(texout, '\v\n'))
    else
      let texout=system("lualatex -interaction=nonstopmode " . bufname("%"))
      silent !start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito "%:p:r:s,$,.pdf,"
    endif
  else
    echo "Not a LaTeX file."
  endif
endfunction

nnoremap <F6> :call Lualatexcurrentfile()<CR>

" BG: b0b0d0
