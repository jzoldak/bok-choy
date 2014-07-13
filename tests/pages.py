"""
Page objects for interacting with the test site.
"""

import os
import time
from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from bok_choy.javascript import js_defined, requirejs, wait_for_js


class SitePage(PageObject):
    """
    Base class for all pages in the test site.
    """

    # Get the server port from the environment
    # (set by the test runner script)
    SERVER_PORT = os.environ.get("SERVER_PORT", 8003)

    def is_browser_on_page(self):
        title = self.name.lower().replace('_', ' ')
        return title in self.browser.title.lower()

    @property
    def url(self):
        return "http://localhost:{0}/{1}".format(self.SERVER_PORT, self.name + ".html")

    @property
    def output(self):
        """
        Return the contents of the "#output" div on the page.
        The fixtures are configured to update this div when the user
        interacts with the page.
        """
        text_list = self.q(css='#output').text

        if len(text_list) < 1:
            return None
        else:
            return text_list[0]


class ButtonPage(SitePage):
    """
    Page for testing button interactions.
    """
    name = "button"

    def click_button(self):
        """
        Click the button on the page, which should cause the JavaScript
        to update the #output div.
        """
        self.q(css='div#fixture input').first.click()


class TextFieldPage(SitePage):
    """
    Page for testing text field interactions.
    """
    name = "text_field"

    def enter_text(self, text):
        """
        Input `text` into the text field on the page.
        """
        self.q(css='#fixture input').fill(text)


class SelectPage(SitePage):
    """
    Page for testing select input interactions.
    """
    name = "select"

    def select_car(self, car_value):
        """
        Select the car with `value` in the drop-down list.
        """
        self.q(css='select[name="cars"] option[value="{}"]'.format(car_value)).first.click()

    def is_car_selected(self, car):
        return self.q(css='select[name="cars"] option[value="{}"]'.format(car)).selected


class CheckboxPage(SitePage):
    """
    Page for testing checkbox interactions.
    """
    name = "checkbox"

    def toggle_pill(self, pill_name):
        """
        Toggle the box for the pill with `pill_name` (red or blue).
        """
        self.q(css="#fixture input#{}".format(pill_name)).first.click()


class AlertPage(SitePage):
    """
    Page for testing alert handling.
    """
    name = "alert"

    def confirm(self):
        with self.handle_alert(confirm=True):
            self.q(css='button#confirm').first.click()

    def cancel(self):
        with self.handle_alert(confirm=False):
            self.q(css='button#confirm').first.click()

    def dismiss(self):
        with self.handle_alert():
            self.q(css='button#alert').first.click()


class SelectorPage(SitePage):
    """
    Page for testing retrieval of information by CSS selectors.
    """

    name = "selector"

    @property
    def num_divs(self):
        """
        Count the number of div.test elements.
        """
        return len(self.q(css='div.test').results)

    @property
    def div_text_list(self):
        """
        Return list of text for each div.test element.
        """
        return self.q(css='div.test').text

    @property
    def div_value_list(self):
        """
        Return list of values for each div.test element.
        """
        return self.q(css='div.test').attrs('value')

    @property
    def div_html_list(self):
        """
        Return list of html for each div.test element.
        """
        return self.q(css='div.test').html

    @property
    def second_inners(self):
        return self.q(css='#o2').first.sub_query(css='div.inner')[0]


class DelayPage(SitePage):
    """
    Page for testing elements that appear after a delay.
    """
    name = "delay"

    def trigger_output(self):
        """
        Wait for click handlers to be installed,
        then click a button and retrieve the output that appears
        after a delay.
        """

        EmptyPromise(self.q(css='div#ready').is_present, "Click ready").fulfill()
        self.q(css='div#fixture button').first.click()
        EmptyPromise(self.q(css='div#output').is_present, "Output available").fulfill()

    def make_broken_promise(self):
        """
        Make a promise that will not be fulfilled.
        Should raise a `BrokenPromise` exception.
        """
        return EmptyPromise(
            self.q(css='div#not_present').is_present, "Invalid div appeared",
            try_limit=3, try_interval=0.01
        ).fulfill()


class SlowPage(SitePage):
    """
    Page that loads its elements slowly.
    """
    name = "slow"

    def is_browser_on_page(self):
        return self.q(css='div#ready').is_present()


class NextPage(SitePage):
    """
    Page that loads another page after a delay.
    """
    name = "next_page"

    def is_browser_on_page(self):
        return self.q(css='#next').is_present()

    def load_next(self, page, delay_sec):
        """
        Load the page named `page_name` after waiting for `delay_sec`.
        """
        time.sleep(delay_sec)
        page.visit()


class VisiblePage(SitePage):
    """
    Page that has some elements visible and others invisible.
    """
    name = "visible"

    def is_visible(self, name):
        """
        Return a boolean indicating whether the given item is visible.
        """
        return self.q(css="div.{}".format(name)).first.visible


@js_defined('test_var1', 'test_var2')
class JavaScriptPage(SitePage):
    """
    Page for testing asynchronous JavaScript.
    """

    name = "javascript"

    @wait_for_js
    def trigger_output(self):
        """
        Click a button which will only work once RequireJS finishes loading.
        """
        self.q(css='div#fixture button').first.click()

    @wait_for_js
    def reload_and_trigger_output(self):
        """
        Reload the page, wait for JS, then trigger the output.
        """
        self.browser.refresh()
        self.wait_for_js()
        self.q(css='div#fixture button').first.click()


@requirejs('main')
class RequireJSPage(SitePage):
    """
    Page for testing asynchronous JavaScript loaded with RequireJS.
    """

    name = "requirejs"

    @property
    @wait_for_js
    def output(self):
        return super(RequireJSPage, self).output


class AjaxPage(SitePage):
    """
    Page for testing an ajax call.
    """

    name = "ajax"

    def click_button(self):
        """
        Click the button on the page, which triggers an ajax
        call that updates the #output div.
        """
        self.q(css='div#fixture button').first.click()


class WaitsPage(SitePage):
    """
    Page for testing wait helpers.
    """

    name = "wait"

    def is_button_output_present(self):
        """
        Click button and wait until output id appears in DOM.
        """
        self.wait_for_element_presence('div#ready', 'Page is Ready')
        self.q(css='div#fixture button').first.click()
        self.wait_for_element_presence('div#output', 'Button Output is Available')

    def is_class_absent(self):
        """
        Click button and wait until playing class disappeared from DOM
        """
        self.q(css='#spinner').first.click()
        self.wait_for_element_absence('.playing', 'Animation Stopped')

    def is_button_output_visible(self):
        """
        Click button and wait until output is displayed.
        """
        self.wait_for_element_presence('div#ready', 'Page is Ready')
        self.q(css='div#fixture button').first.click()
        self.wait_for_element_visibility('div#output', 'Button Output is Visible')

    def is_spinner_invisible(self):
        """
        Click button and wait until spinner is disappeared.
        """
        self.q(css='#spinner').first.click()
        self.wait_for_element_invisibility('#anim', 'Button Output is Visible')
