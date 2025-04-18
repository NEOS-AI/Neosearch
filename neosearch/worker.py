from dotenv import load_dotenv
import sys
import warnings
from faststream import FastStream

# Load environment variables
load_dotenv()

# Ignore warnings
warnings.filterwarnings("ignore")

# Add the root directory to the path so that we can import the settings
sys.path.append("..")

# custom module
from neosearch.constants.queue import USE_QUEUE  # noqa: E402
from neosearch.app.worker_broker import get_worker_broker  # noqa: E402

if not USE_QUEUE:
    raise Exception("Queue is not enabled")

# init broker
broker = get_worker_broker()

# init faststream app
app = FastStream(broker)


if __name__ == "__main__":
    from neosearch.engine.agents.deep_research import background_research_task  # noqa: E402
    # app.run()
    background_research_task("task_id", "How to build a google-level search engine?")
