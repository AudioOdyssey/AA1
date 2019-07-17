import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"./audio_od")
from main import app as application
application.secret_key = b"jk_\xf7\xa7':\xea$/\x88\xc0\xa3\x0e:d"

application.run()
