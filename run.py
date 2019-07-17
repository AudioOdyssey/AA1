import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"./audio_od")
from main import app as application

application.run(debug=True)
