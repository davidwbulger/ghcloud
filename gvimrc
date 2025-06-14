if has('gui_running')
  set guifont=Consolas:h14:b:cANSI:qDRAFT
endif

" COLOURS THE BACKGROUND IF THE LAST LINE CONTAINS 'BG: [hex colour code]' (SEE, E.G., THE END OF THIS FILE):
" Default bg first:
highlight normal guibg=#bbaa99
autocmd BufRead * $ya z | if @z =~# ' BG:' | let @z = substitute(@z, '^.* BG:\s*#\=\(\<.*\>\).*$', 'highlight Normal guibg=#\1', 'g') | execute @z | endif
autocmd BufRead * $ya z | if @z =~# ' FG:' | let @z = substitute(@z, '^.* FG:\s*#\=\(\<.*\>\).*$', 'highlight Normal guifg=#\1', 'g') | execute @z | endif

set vb t_vb=

set guioptions-=m
set guioptions-=T

set columns=85
set lines=56

" These convenience window-layout commands are a bit crude & will fail if,
" e.g., there are already some splits. Mainly intended for use on first opening
" a file for editing.
nnoremap <F12> :set columns=171<CR>:while tabpagewinnr(1,'$')<2<CR>vsplit<CR>endwhile<CR><CR>
nnoremap <F11> :set guifont=Consolas:h13:b:cANSI:qDRAFT<CR>
nnoremap <F10> :set guifont=Consolas:h13:b:cANSI:qDRAFT<CR>:set columns=257<CR>:while tabpagewinnr(1,'$')<3<CR>vsplit<CR>endwhile<CR><CR>
nnoremap <F9> :execute printf('highlight Normal guibg=#%x%x%x',160+rand()%96,160+rand()%96,160+rand()%96)<CR><CR>
nnoremap <F9> :let red=rand()%96 <bar> :let green=rand()%96 <bar> :let blue=rand()%96 <bar> execute printf('highlight Normal guibg=#%x%x%x',160+red,160+green,160+blue) <bar> execute printf('highlight Normal guifg=#%02x%02x%02x',red,green,blue)<CR><CR>

" BG: b0b0d0
