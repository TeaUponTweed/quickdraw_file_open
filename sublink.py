import sublime
import sublime_plugin
import os

class OpenFileUnderCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the current selection
        selection = self.view.sel()[0]

        # Expand the selection to cover the whole word or file path
        self.expanded_region = self.view.expand_by_class(selection, sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, " /\\")
        file_name = self.view.substr(self.expanded_region)

        # Remove any leading/trailing whitespaces, brackets, or quotes
        file_name = file_name.strip(" '\"[]()<>")

        # List all files in the project folders
        window = self.view.window()
        project_data = window.project_data() if window else None
        project_folders = project_data['folders'] if project_data and 'folders' in project_data else []

        self.file_list = []
        for directory in project_folders:
            path = directory['path']
            for root, _, files in os.walk(path):
                for file in files:
                    if file.startswith(file_name):
                        abs_path = os.path.abspath(os.path.join(root, file))
                        self.file_list.append(abs_path)
        # Show quick panel with fuzzy search
        if len(self.file_list) > 1:
            items = [f for f in self.file_list]
            window.show_quick_panel(items, self.on_select, 0, -1, self.on_highlighted)
        elif len(self.file_list) == 1:
            self.view.window().open_file(self.file_list[0])
        else:
            sublime.error_message('File not found: {}'.format(file_name))

    def on_select(self, index):
        if index >= 0:
            selected_file_path = self.file_list[index]
            self.view.window().open_file(selected_file_path)
            self.view.run_command("replace_text", {"region": (self.expanded_region.a, self.expanded_region.b), "text": os.path.basename(selected_file_path)})

    def on_highlighted(self, index):
        if index >= 0:
            selected_file_path = self.file_list[index]
            self.view.window().open_file(selected_file_path,flags=4)
