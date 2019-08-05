import time
import tkinter
import tkinter.messagebox
import pickle

'''
Current Version: 0.1.3
'''

'''
BUGS:
Might not be compatible with UNIX OS. This is due to the difference between windows and UNIX path system,
So Loading and Saving progress might cause crashes on non WIN systems'''

''' 
NEXT VERSION (0.1.4):
1. Code review
2. Basic Documentation
3. Add exception (Single type)
'''

'''
Ideas for near future:
12. Upon pausing a session - rename Start button to Resume
13. Render irrelevant buttons unclickable when relevant
11. Add a method to which you give time by epoch and it translates it into a string
8. smart login - user can put username and continue. you can give a password, but don't have to
10. make an executable file for the project
9. always on top toggle
7. git repository
14. Add an indicator of the current status
* Add a drop down menu to allow user to choose a category for his session
* Add an option to create new categories
* Allow continuing from a closed running or paused session
'''

'''
Changelog:
0.1.1 - Start, Stop, View (cmd)
0.1.2 - Added giu
0.1.3 - 
    1. Added autosave of progress into an extrenal file
    2. Auto load progress from file when opening
0.1.4 - 
    1. Added a pause button, allowing to pause a session and resume it later
    2. Added a reset button, allowing to reset the total time displayed
    Bug Fixes:
        * Starting a Session after a pause increases the total time
        * When starting after reset the total timer returns to it's previous time
        * issue with START -> PAUSE -> STOP -> START increasing total time resolved  
'''


class SessionMaster:

    INFO = "This is a Time Machine.\n" \
           "Remember: There is no going back in time."

    class Session:

        STOPPED = 0
        RUNNING = 1
        PAUSED = 2

        def __init__(self, sess_num, cat="default"):
            self.sess_num = sess_num
            self.category = cat
            self.status = SessionMaster.Session.STOPPED
            self.start_ticks = None
            self.end_ticks = None
            self.total_ticks = 0
            self.rating = None

        def start(self):
            self.start_ticks = time.time()
            self.status = SessionMaster.Session.RUNNING

        def pause(self):
            self.status = SessionMaster.Session.PAUSED
            self.end_ticks = time.time()
            self.total_ticks += int(self.end_ticks - self.start_ticks)

        def stop(self, rating=None):
            self.end_ticks = time.time()
            if rating:
                self.rating = rating
            if self.get_status() == SessionMaster.Session.RUNNING:
                self.total_ticks += int(self.end_ticks - self.start_ticks)
            self.status = SessionMaster.Session.STOPPED

        def get_start_time(self):
            return self.start_ticks

        def get_status(self):
            return self.status

        def get_id(self):
            return self.sess_num

        def get_total(self):
            ticks = self.total_ticks
            if self.status == SessionMaster.Session.RUNNING:
                ticks += time.time() - self.start_ticks
            return ticks

        def __repr__(self):
            return "Session #{0}: Cat: {1}, Start: {2}, End: {3}, Total: {4}, Rating: {5}".format(
                self.sess_num, self.category, time.strftime('%H:%M:%S', time.gmtime(self.start_ticks)),
                time.strftime('%H:%M:%S', time.gmtime(self.end_ticks)),
                time.strftime('%H:%M:%S', time.gmtime(self.get_total())), self.rating)

    def __init__(self):
        self.history = []
        self.curr_sess = None
        self.last_reset = 0
        self.in_sess = False  # Remove this and when terminating a session update self.curr_sess to None
        # Can create a status function that refers to curr_sess
        self.load()

        self.root_tk = tkinter.Tk()
        # self.init_gui(self.root_tk)
        self.info = tkinter.Button(self.root_tk, text="Info", command=self.display_info)
        self.info.pack()
        self.session_time = tkinter.Label(text="Current session: " + time.strftime('%H:%M:%S', time.gmtime(0)))  # don't like it
        self.session_time.pack()
        self.total_time = tkinter.Label(text="Completed: " + time.strftime('%H:%M:%S', time.gmtime(self.get_total())))
        self.total_time.pack()
        self.start_bot = tkinter.Button(self.root_tk, text="Start", command=self.start)
        self.start_bot.pack()
        self.pause_bot = tkinter.Button(self.root_tk, text="Pause", command=self.pause)
        self.pause_bot.pack()
        self.stop_bot = tkinter.Button(self.root_tk, text="Stop", command=self.stop)
        self.stop_bot.pack()
        self.reset_bot = tkinter.Button(self.root_tk, text="Reset", command=self.reset)
        self.reset_bot.pack()
        self.refresh()
        self.root_tk.mainloop()

    def __repr__(self):
        repr_str = "Here is your progress - Total time: {0}, Sessions: {1}, Session History:".\
            format(time.strftime('%H:%M:%S', time.gmtime(self.get_total())), len(self.history))
        for sess in self.history:
            repr_str += "\n"+sess.__repr__()
        return repr_str

    @staticmethod
    def display_info():
        tkinter.messagebox.showinfo("Info", SessionMaster.INFO)

    def load(self):
        try:
            with open("history.pickle", 'rb') as history_handle:
                self.history = pickle.load(history_handle)
        except IOError:
            print("No saved progress found")
        try:
            with open("reset.pickle", 'rb') as reset_handle:
                self.last_reset = pickle.load(reset_handle)
        except IOError:
            pass  # This happens when the client never received a reset command

    def save(self):
        with open('history.pickle', 'wb') as history_handle:
            pickle.dump(self.history, history_handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open('reset.pickle', 'wb') as reset_handle:
            pickle.dump(self.last_reset, reset_handle, protocol=pickle.HIGHEST_PROTOCOL)

    def start(self):
        if self.in_sess:
            if self.curr_sess.get_status() == SessionMaster.Session.PAUSED:
                self.curr_sess.start()
                self.refresh()
                print("Resuming session")
                return
            elif self.curr_sess.get_status() == SessionMaster.Session.RUNNING:
                print("You are already in a session")
                return
            else:
                print("error")
                exit(1)
        self.in_sess = True
        self.curr_sess = SessionMaster.Session(len(self.history)+1)
        self.curr_sess.start()
        self.refresh()
        print("Session {0} Started.".format(self.curr_sess.get_id()))

    def pause(self):
        if not self.in_sess or not self.curr_sess:
            print("There is no active session")
            return False
        if self.curr_sess.get_status() == SessionMaster.Session.PAUSED:
            print("Session is already paused")
            return False
        self.curr_sess.pause()
        print("Session Paused")
        return True

    def stop(self):
        if not self.in_sess or not self.curr_sess:
            print("There is no active session")
            return False
        self.curr_sess.stop()
        self.history.append(self.curr_sess)
        self.in_sess = False
        self.save()
        print("Session {0} Stopped.".format(self.curr_sess.get_id()))
        # print(self)  # Prints full history
        return True

    def get_total(self):
        total = 0
        for sess in self.history:
            if sess.get_start_time() > self.last_reset:
                total += sess.get_total()
        if self.in_sess:
            total += self.curr_sess.get_total()
        return total

    def set_session_timer(self, new_time):
        self.session_time.configure(text="Current session: " +
                                         time.strftime('%H:%M:%S', time.gmtime(new_time)))

    def set_total_timer(self, new_time):
        self.total_time.configure(text="Completed: " +
                                       time.strftime('%H:%M:%S', time.gmtime(new_time)))

    def refresh(self):
        if self.in_sess:
            self.set_session_timer(self.curr_sess.get_total())
            self.set_total_timer(self.get_total())
            self.root_tk.after(10, self.refresh)

    def reset(self):
        self.last_reset = time.time()
        if self.in_sess and self.curr_sess.get_status():
            self.stop()
        else:
            self.save()
        self.set_total_timer(0)
        print("Counter Reset")


session = SessionMaster()
