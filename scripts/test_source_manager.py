from logger import logger
from source_manager import SourceManager


manager = SourceManager()

sources = manager.get_active_sources()

logger.info("Sources actives : %s", len(sources))

for source in sources:

    logger.info(
        "%s | priorité=%s",
        source["name"],
        source["priority"],
    )