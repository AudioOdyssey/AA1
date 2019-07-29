import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"./audio_od")
from audio_od import app as application

if __name__=="__main__":
	application.run(debug=True)
