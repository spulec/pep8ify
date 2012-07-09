
is_android = True
try:
   import shutil
   # this comment should be intended to `import` and `if`
 # this ono, too
    # this comment should be intended, too
   if xxxx + 1:
      if yyyyy * 2:
         if zzzz / 3:
            aaaaa + 4
      # this should stay at `yyyy` level
   elif kkkk - 5:
      if lll + 6:
         mmmm * 7
         # this should stay at `mmm * 7` level
      nnnn / 8
   elif kkkk + 9:
      if lll - 10:
         mmmm * 11
         # this should stay at `mmm * 11` level
   else:
      # this should stay at `bbbb` level
      bbbb / 12
   # this should go to `eeee` level
   eeee
except ImportError:
    pass
