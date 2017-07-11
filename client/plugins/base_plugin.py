"""
Base plugin file.
They just need a run method and an INTERVAL int interval.
"""

# Import what you like here



# set an interval in seconds
INTERVAL = 1000
CATEGORY = 'default'


# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """
    return {}


if __name__ == '__main__':
    print run()
