import tkinter as tk
import requesttab
import stashcount
import filterupdate
from shutil import copyfile




#TO DO:
# - Save and load settings from File
# - color highlightning of entry-fields and labels
class Settings(tk.Toplevel):
    def __init__(self, parent, current_settings):
        super().__init__()
        self.title("Settings")
        self.parent = parent
        self.current_settings = current_settings
        # --- Functionality ---
        #Account Name
        self.accountNameLabel = tk.Label(self, text = "Account Name:")
        self.accountName = tk.Entry(self)
        self.accountName.insert(0, self.current_settings['AccountName'])

        #SessionID
        self.sessionIdLabel = tk.Label(self, text = "SessionID:")
        self.sessionId = tk.Entry(self)
        self.sessionId.insert(0, self.current_settings['SessionID'])

        # Strictness Level:
        self.strictness_label = tk.Label(self, text = 'Strictness:')
        self.strictness = tk.StringVar()
        self.strictness.set(self.current_settings['Strictness'])
        self.strictness_levels = ['0', '1', '2', '3', '4', '5', '6']
        self.strictness_selector = tk.OptionMenu(self, self.strictness, *self.strictness_levels)

        #Query-Tab:
        self.tabLabel = tk.Label(self, text = "Tab for Query:")
        self.tab = tk.Entry(self)
        self.tab.insert(0, self.current_settings['Tab'])

        #Number of Chaos Sets
        self.maxChaosLabel = tk.Label(self, text = "Max. Chaos-Recipe-Sets:")
        self.chaosSets = tk.StringVar()
        self.chaosSetOptions = [str(x) for x in range(1, 11)]
        self.chaosSets.set(self.current_settings['maxChaosRecipes'])
        self.chaosSets_selector = tk.OptionMenu(self, self.chaosSets, *self.chaosSetOptions)

        #Selecting League
        self.leagueLabel = tk.Label(self, text = "League:")
        self.league = tk.StringVar()
        self.league.set(self.current_settings['League'])
        self.leagues = ['Standard', 'Heist']# should request changing names from API
        self.league_selector = tk.OptionMenu(self, self.league, *self.leagues)

        # Save Settigns
        self.save_and_return = tk.Button(self, text = "save and return", command = lambda: self.save())


        # --- Layout ---
        #Since it's just one Column: pack() does the job.

        #Account
        self.accountNameLabel.pack(side = tk.TOP, fill = tk.X)
        self.accountName.pack(side = tk.TOP, fill = tk.X)
        #SessionID
        self.sessionIdLabel.pack(side = tk.TOP, fill = tk.X)
        self.sessionId.pack(side = tk.TOP, fill = tk.X)
        #strictness
        self.strictness_label.pack(side = tk.TOP, fill = tk.X)
        self.strictness_selector.pack(side = tk.TOP, fill = tk.X)
        #Tab
        self.tabLabel.pack(side = tk.TOP, fill = tk.X)
        self.tab.pack(side = tk.TOP, fill = tk.X)
        #ChaosSets
        self.maxChaosLabel.pack(side = tk.TOP, fill = tk.X)
        self.chaosSets_selector.pack(side = tk.TOP, fill = tk.X)
        #League
        self.leagueLabel.pack(side = tk.TOP, fill = tk.X)
        self.league_selector.pack(side = tk.TOP, fill = tk.X)
        #Save
        self.save_and_return.pack(side = tk.TOP, fill = tk.X)

    #could have control wether or not settings are "complete"
    def save(self):
        #Storing selected Settings in parents current_settings dict()
        self.current_settings['AccountName'] = self.accountName.get()
        self.current_settings['SessionID'] = self.sessionId.get()
        self.current_settings['Strictness'] = self.strictness.get()
        self.current_settings['Tab'] = self.tab.get()
        self.current_settings['maxChaosRecipes'] = self.chaosSets.get()
        self.current_settings['League'] = self.league.get()


        print('-- Settings Window ---')
        print(self.current_settings)


        #sending current_settings back to parent:
        self.parent.update_settings(self.current_settings)
        #closing settings window:
        self.destroy()


#To Do
# - connecting to stash-Request
# - Error Handling for bad requests, trying to tell the user whats wrong

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChaosFilter")
        self.geometry('70x50')
        self.attributes("-topmost", True)
        #self.wm_attributes("-alpha", 0.5) #making it Transparent
        self.settings = None
        self.current_settings = {
            'AccountName' : '',
            'SessionID': '',
            'Strictness': '1',
            'Tab': '0',
            'maxChaosRecipes': '4',
            'League': 'Standard'
            }

        self.stash_tab = None
        self.base_count = None#self.count()

        # --- Functionality ---
        # Filter Reload
        self.reload = tk.Button(self, text = 'Reload', command = lambda: self.reload_filter())

        #settings
        self.settings_button = tk.Button(self, text = 'Settings', command = lambda: self.open_settings_menu())

        # --- Layout ---
        self.settings_button.pack(side = tk.TOP, fill = tk.X)
        self.reload.pack(side = tk.TOP, fill = tk.X)

        #test:
        #self.test = tk.Button(self, text = 'Test', command = lambda: self.print())
        #self.test.pack()

        #starting the App
        root.mainloop()


    def print(self):
        print(self.current_settings)


    def open_settings_menu(self):
        try:
            if self.settings.state() == 'normal':
                self.settings.focus()
        except:
            self.settings = Settings(self, self.current_settings)


    def update_settings(self, current_settings):
        self.current_settings = current_settings


    def reload_filter(self):
        #requesting StashTab Json from POE API
        print(self.current_settings)

        if self.stash_tab is None:
            self.stash_tab = requesttab.requesttab(settings = self.current_settings)
        else:
            self.stash_tab.update(settings = self.current_settings)

        #couting the base items in given JSON
        self.count()

        #updating the .filter File and copying it to the game-folder
        filterupdate.filterupdate(count = self.base_count,
            max_count = self.current_settings.get('maxChaosRecipes'),
            strictness = self.current_settings.get('Strictness'))
        self.copy_filter_to_gamefolder()
        print('--- updated ---')
        print()
        print()

    def count(self):
        cur_count = stashcount.stashcount(json_file = self.stash_tab.data)
        cur_count.count()
        self.base_count = cur_count.base_count
        del cur_count


    def copy_filter_to_gamefolder(self):
        src = 'filters/current_filter/chaos_recipes.filter'
        dst = './test/test.filter'
        copyfile(src, dst)


def main():
    root = App()



if __name__ == '__main__':
    main()
