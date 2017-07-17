import sys, tty, termios
from datetime import datetime

# sort
Ascending = 0
Descending = 1

# group
Standard = 0    # years, then weeks, then days for next 7 from today
Years = 1
Months = 2
Weeks = 3
Days = 4

class TodoItem:
    def __init__(self, checked=False, datetime=datetime.now(), precision='YMD',
        content='Untitled item'):
        self.checked = checked
        self.datetime = datetime
        self.precision = precision
        self.content = content

    def toggle(self):
        self.checked = not self.checked

    def render(self):
        if self.checked:
            print("[✔] %s" % self.content, end="")
        else:
            print("[ ] %s" % self.content, end="")

class Line:
    def __init__(self, content="", underline=False):
        self.content = content
        self.underline = underline

    def render(self):
        if self.underline:
            print("\033[4m", end="")

        print(self.content, end="")
        print("\033[24m", end="")

class TodoList:
    def __init__(self, sort=Ascending, group=Standard):
        self.sort = sort
        self.group = group
        self.cursor = 0
        self.screenTop = 0
        self.screenHeight = 35
        self.screenItems = [
            Line("Group 1", underline=True),
            Line(),
            TodoItem(False, datetime(year=2017, month=7, day=10, hour=3, minute=30),
                    'YMDhm', "Do this one thing"),
            TodoItem(False, datetime(year=2017, month=7, day=11, hour=3, minute=40),
                'YMDhm', "Do this other thing"),
            Line(),
            Line("Group 2", underline=True),
            Line(),
            TodoItem(True, datetime(year=2018, month=1, day=1), 'Y', 
                "Do this last thing sometime")
        ]

    def scroll(self, n):
        i = self.cursor + n
        while i >= 0 and i < len(self.screenItems):
            if isinstance(self.screenItems[i], TodoItem):
                self.cursor = i
                break
            i += 1 if n > 0 else -1

    def toggleSelected(self):
        if isinstance(self.screenItems[self.cursor], TodoItem):
            self.screenItems[self.cursor].toggle()

    def render(self):
        print("\033[2J", end="") # erase all
        sys.stdout.flush()

        j = self.screenTop
        while j < self.screenTop + self.screenHeight:
            if j >= len(self.screenItems):
                break

            if j == self.cursor:
                print("\033[100m", end="")

            y = j - self.screenTop + 1
            print("\033[%d;%dH" % (y,1), end="")
            self.screenItems[j].render()
            print("\033[40m", end="")
            j += 1
        
        sys.stdout.flush()

def getsize():
    print("\033[999;999H", end="")
    print("\033[6n", end="")
    sys.stdout.flush()

def match_ansi_escape():
    ch1 = sys.stdin.read(1)
    if ch1 == '[':
        ch2 = sys.stdin.read(1)
        if ch2 == 'A': 
            return 'up'
        elif ch2 == 'B': 
            return 'down'

def render_help():
    print("\033[999;1H", end="") # move to bottom
    print("\033[7m", end="") # inverse
    print("<Up>/<Down>:scroll <Space>:toggle", end="")
    print("\033[0m", end="")
    sys.stdout.flush()

if __name__ == "__main__":
    print("\033[?1049h", end="") # enter alternate screen buffer
    print("\033[?25l", end="") # hide cursor
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    tui = TodoList()

    try:
        tty.setraw(sys.stdin.fileno())
        while 1:
            tui.render()
            render_help()

            ch = sys.stdin.read(1)
            if ch == '\033':
                ch = match_ansi_escape()

            if ch == 'q':
                break
            elif ch == ' ':
                tui.toggleSelected()
            elif ch == 'up':
                tui.scroll(-1)
            elif ch == 'down':
                tui.scroll(+1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)
        print("\033[?25h", end="") # show cursor
        print("\033[?1049l", end="") # leave alternate screen buffer

