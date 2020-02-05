from tools import config
from tools.session import Session

config.DEBUG = True


s2 = Session(0, 1)

from bots import bowstringer
jeff = bowstringer.Bowstringer(s2)
jeff.startup()
jeff.run()