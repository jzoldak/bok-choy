"""
Base class for testing a web application.
"""
import sys
import os
import json
from unittest import TestCase
from abc import ABCMeta
from uuid import uuid4
from .browser import browser, save_screenshot
from browsermobproxy import Server


class WebAppTest(TestCase):
    """
    Base class for testing a web application.
    """

    __metaclass__ = ABCMeta

    # Execute tests in parallel!
    _multiprocess_can_split_ = True

    def setUp(self):
        """
        Start the browser for use by the test.
        You *must* call this in the `setUp` method of any subclasses before using the browser!

        Returns:
            None
        """
        # Start up the browsermob proxy so that we can save HAR file for profiling
        server = Server('browsermob-proxy')
        server.start()
        self.proxy = server.create_proxy()

        # If using SauceLabs, tag the job with test info
        tags = [self.id()]

        # Set up the page objects
        # This will start the browser, so add a cleanup
        self.browser = browser(tags=tags, proxy=self.proxy)

        # Cleanups are executed in LIFO order.
        # This ensures that the screenshot is taken BEFORE the browser quits.
        self.addCleanup(server.stop)
        self.addCleanup(self.browser.quit)
        self.addCleanup(self._screenshot)

    @property
    def unique_id(self):
        """
        Helper method to return a uuid.

        Returns:
            39-char UUID string
        """
        return str(uuid4().int)

    def _screenshot(self):
        """
        Take a screenshot on failure or error.
        """
        # Determine whether the test case succeeded or failed
        result = sys.exc_info()

        # If it failed, take a screenshot
        # The exception info will either be an assertion error (on failure)
        # or an actual exception (on error)
        if result != (None, None, None):
            try:
                save_screenshot(self.browser, self.id())
            except:
                pass

    def save_har_file(self, har, name):
        """
        Save a HAR file.

        The location of the har file can be configured
        by the environment variable `HAR_DIR`.  If not set,
        this defaults to the current working directory.

        Args:
            proxy: The browsermob proxy.
            name (str): A name for the har file, which will be used in the output file name.

        Returns:
            None
        """
        har_file = os.path.join(os.environ.get('HAR_DIR', ''), '{}.har'.format(name))
        with open(har_file, 'w') as output_file:
            json.dump(har, output_file)
