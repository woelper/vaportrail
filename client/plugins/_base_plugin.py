"""
Base plugin file.
They just need a run method and an INTERVAL int interval.
"""

# Import what you like here



# set an interval in seconds, fractions allowed
INTERVAL = 1000.0
CATEGORY = None

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary. Empty dicts or no return value will be ignored
    and the plugin will be run at next INTERVAL.
    You can use this to test for events and just return a valid dict if you match your criteria.
    """

    return {}


if __name__ == '__main__':
    print run()
