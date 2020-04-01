# Adapted from https://github.com/sphinx-contrib/redirects

import os
import re

from sphinx.builders import html as builders
from sphinx.util import logging as logging

TEMPLATE = '<html><head><meta http-equiv="refresh" content="0; url=%s"/></head></html>'

logger = logging.getLogger(__name__)

def generate_redirects(app):
    path = os.path.join(app.srcdir, app.config.redirects_file)
    if not os.path.exists(path):
        logger.info("Could not find redirects file at '%s'", path)
        return

    source_suffix = next(iter(app.config.source_suffix))

    if not type(app.builder) == builders.StandaloneHTMLBuilder:
        logger.info("Redirects are only supported by the 'html' builder. Skipping...")
        return

    with open(path) as redirects:
        pattern = re.compile(r"^([\w\-./ ]+)(#.*)?$")
        for line in redirects.readlines():
            # Exclude comment or empty lines
            match_result = pattern.search(line)
            if not match_result:
                continue

            # Parse the rule
            redirect = match_result.group(1).rstrip()
            if redirect.count(' ') != 1:
                logger.error("Ignoring malformed redirection: %s", redirect)
                continue
            from_path, to_path = redirect.split()
            logger.debug("Redirecting '%s' to '%s'", from_path, to_path)

            # Prepare source and destination paths
            from_path = from_path.replace(source_suffix, '.html')
            to_path = to_path.replace(source_suffix, '.html')
            absolute_from_path = os.path.join(app.builder.outdir, from_path)
            absolute_to_path = os.path.join(app.builder.outdir, to_path)
            from_directory = os.path.dirname(absolute_from_path)
            if not os.path.exists(from_directory):
                os.makedirs(from_directory)

            # Create the redirection
            with open(absolute_from_path, 'w') as f:
                f.write(TEMPLATE % absolute_to_path)


def setup(app):
    app.add_config_value('redirects_file', 'redirects', 'env')
    app.connect('builder-inited', generate_redirects)
