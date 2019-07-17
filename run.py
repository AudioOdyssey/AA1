import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"./audio_od")
from main import app as application
application.secret_key = b"()Hdy)(D^tUBTyi*T*tgI*B"

application.run(debug=True)
