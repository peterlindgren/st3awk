import sublime, sublime_plugin, os, sys, traceback, tempfile
from subprocess import Popen, PIPE, STDOUT, call, DEVNULL

global_awk = None

def check_awk_executable():
    settings = sublime.load_settings("awk.sublime-settings")
    awk = settings.get('awk', 'awk.exe' if sys.platform == 'win32' else 'awk')

    global global_awk
    if global_awk == awk:
        return True

    try:
        ret = call([awk, '--version'], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, shell=True)
        global_awk = awk
    except FileNotFoundError as e:
        pass
    except Exception as e:
        sublime.error_message(traceback.format_exc())

    return global_awk != None

def get_script_path():
    settings = sublime.load_settings("awk.sublime-settings")
    script_path = settings.get("script_path", "User/awk_script.awk")
    path_tuple = os.path.split(script_path)
    packages_path = sublime.packages_path()
    awk_path = os.path.abspath(os.path.join(packages_path, *path_tuple))
    return awk_path

def get_expr():
    settings = sublime.load_settings("awk.sublime-settings")
    expr = settings.get("expr", "{print $1}")
    return expr

def set_expr(expr):
    settings = sublime.load_settings("awk.sublime-settings")
    settings.set("expr", expr)
    sublime.save_settings("awk.sublime-settings")

class AwkRunActionCommand(sublime_plugin.TextCommand):
    def run(self, edit, expr=None, inplace=True, script=None):
        if expr == None and script == None:
            sublime.error_message('awk_run_action: invalid arguments, missing expr or script')
            return

        regions = [r for r in self.view.sel() if not r.empty()]
        if len(regions) == 0:
            regions = [sublime.Region(0, self.view.size())]

        texts = [self.view.substr(r) for r in regions]
        for i, text in enumerate(texts):
            try:
                args = ['awk', expr or '--file=%s' % script]
                p = Popen(args, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                out, err = p.communicate(input=bytes(text, 'utf-8'))
                out = out.decode('utf-8').replace('\r', '')

                if p.returncode != 0 or err != b'':
                    err = err.decode('utf-8').replace('\r', '')
                    sublime.error_message('Error when run awk: %s' % err)
                    return

                texts[i] = out.rstrip(os.linesep)

            except Exception as e:
                sublime.error_message(traceback.format_exc())
                return

        if inplace:
            for i, text in reversed(list(enumerate(texts))):
                self.view.replace(edit, regions[i], text)
            return

        syntax = self.view.settings().get('syntax')

        new_view = self.view.window().new_file()
        new_view.assign_syntax(syntax)
        content = os.linesep.join(texts).replace('\r', '')
        new_view.insert(edit, 0, content)

class AwkRunCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        if not check_awk_executable():
            sublime.error_message("awk is required on PATH")
            return

        inplace = args.get('inplace', False) == True

        if args.get('script', False) == True:
            awk_path = get_script_path()
            self.view.run_command("awk_run_action", {
                "script": awk_path,
                "inplace": inplace
            })
            return

        def onDone(expr):
            set_expr(expr)
            if not self.view.is_valid():
                sublime.error_message("Awk: View was closed before awk input panel completed")
                return

            if '\n' in expr:
                temp_path = os.path.join(tempfile.gettempdir(), "sublime_text_awk_temp.awk")
                with open(temp_path, 'w+', encoding='utf-8') as f:
                    f.write(expr)
                self.view.run_command("awk_run_action", {
                    "script": temp_path,
                    "inplace": inplace
                })
                return

            self.view.run_command("awk_run_action", {
                "expr": expr,
                "inplace": inplace
            })

        expr = get_expr()
        self.view.window().show_input_panel('Awk:', expr, onDone, None, None)

class AwkScriptCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        if not check_awk_executable():
            sublime.error_message("awk is required on PATH")
            return
        inplace = args.get('inplace', False) == True
        awk_path = get_script_path()
        self.view.run_command("awk_run_action", {
            "script": awk_path,
            "inplace": inplace
        })

class AwkOpenCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        awk_path = script_path()
        if not os.path.isfile(awk_path):
            try:
                with open(awk_path, 'w+', encoding='utf-8') as f:
                    pass
            except Exception as e:
                sublime.error_message(traceback.format_exc())
                return

        self.view.window().open_file(awk_path)
