#
# Test mixed intents
#

if True:
  if (x == 5 or x == 7):
        print "ping"

if True:
    if (x == 5 or x == 7):
      print "ping"


def testing_func():
    if True:
      if (x == 5 or x == 7):
            print "ping"

    if True:
        if (x == 5 or x == 7):
          print "ping"


def testing_func2():
  if True:
    if (x == 5 or x == 7):
          print "ping"

  if True:
      if (x == 5 or x == 7):
        print "ping"
