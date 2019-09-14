import yaml
import logging
import os

from typing import Dict

logger = logging.getLogger(__name__)

CREDS_FILE_ENV_VAR = 'NLPSERVICE_TWITTER_CREDS_FILE'

DEFAULT_CREDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'creds.yml')

# credentials type
Creds = Dict[str, str]


def creds() -> Creds:
    """
    Return twitter credentials.  For now this just looks for a creds.yml file
    in this module's parent directory.

    :return: dict of credentials that can be passed to the twitter.API constructor
    """
    creds_yml = os.getenv(CREDS_FILE_ENV_VAR) or DEFAULT_CREDS_FILE

    with open(creds_yml, 'r') as fp:
        # TODO: check that all credentials exist
        return yaml.load(fp)
