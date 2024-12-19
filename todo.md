Prevent leaderboard not saving
```py
import atexit
@atexit.register
def goodbye():
    # cleanup processes here
    print('You are now leaving the Python sector.')
```
