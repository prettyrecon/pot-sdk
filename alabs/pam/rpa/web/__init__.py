
from selenium import webdriver


################################################################################
def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
    from selenium.webdriver.common.desired_capabilities import \
        DesiredCapabilities
    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"  # complete
    # caps["pageLoadStrategy"] = "eager"  #  interactive
    caps["pageLoadStrategy"] = "none"

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url,
                                  desired_capabilities=caps)
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver