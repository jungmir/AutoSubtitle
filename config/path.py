# DATA path
from pathlib import Path
import os

data_path = (Path(os.path.dirname(__file__)) / '..' / 'temp').resolve()

video_path = data_path / 'videos'