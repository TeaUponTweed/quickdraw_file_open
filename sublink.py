import sublime
import sublime_plugin
import os

class OpenFileUnderCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the current selection
        selection = self.view.sel()[0]

        # Expand the selection to cover the whole word or file path
        self.expanded_region = self.view.expand_by_class(selection, sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, " ()[]\"'")
        file_name = self.view.substr(self.expanded_region)

        # Remove any leading/trailing whitespaces, brackets, or quotes
        file_name = file_name.strip(" '\"[]()<>\n")

        # List all files in the project folders
        window = self.view.window()
        project_data = window.project_data() if window else None
        project_folders = project_data['folders'] if project_data and 'folders' in project_data else []
        # self.file_list = {}
        matching_file = None
        for directory in project_folders:
            path = directory['path']
            for root, _, files in os.walk(path):
                if '.git/' in root:
                    continue
                for file in files:
                    abs_path = os.path.abspath(os.path.join(root, file))
                    rel_path = os.path.relpath(abs_path, path)
                    if rel_path == file_name:
                        matching_file = abs_path
                        break
                    if abs_path == file_name:
                        matching_file = abs_path
                        break

                    # self.file_list[abs_path] = rel_path
        if matching_file is not None:
            self.view.window().open_file(matching_file)
        else:
            sublime.error_message('File not found: {}'.format(file_name))
        # test.txt
        # testdir/test2.txt
        # "test.txt"
        # 'testdir/test2.txt'
        # [testdir/test2.txt]
        # do_things_to("testdir/test2.txt")
        # # Show quick panel with fuzzy search
        # if len(self.file_list) > 1:
        #     items = [f for f in self.file_list]
        #     window.show_quick_panel(items, self.on_select, 0, -1, self.on_highlighted)
        # elif len(self.file_list) == 1:
        #     self.view.window().open_file(self.file_list[0])
        # else:
        #     sublime.error_message('File not found: {}'.format(file_name))

class FuzzyFileSplatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the current selection
        selection = self.view.sel()[0]
        # Expand the selection to cover the whole word or file path
        self.expanded_region = self.view.expand_by_class(selection, sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, " ()[]\"'")
        file_name = self.view.substr(self.expanded_region)

        # Remove any leading/trailing whitespaces, brackets, or quotes
        file_name = file_name.strip(" '\"[]()<>\n")

        # List all files in the project folders
        window = self.view.window()
        project_data = window.project_data() if window else None
        project_folders = project_data['folders'] if project_data and 'folders' in project_data else []
        # self.rel_to_abs_map = {}
        self.rel_paths = []
        # matching_file = None
        for directory in project_folders:
            path = directory['path']
            for root, _, files in os.walk(path):
                if '.git/' in root:
                    continue
                for file in files:
                    abs_path = os.path.abspath(os.path.join(root, file))
                    rel_path = os.path.relpath(abs_path, path)
                    # self.rel_to_abs_map[rel_path] = abs_path
                    self.rel_paths.append(rel_path)
        # if matching_file is not None:
        #     self.view.window().open_file(matching_file)
        # else:
        #     sublime.error_message('File not found: {}'.format(file_name))
        # test.txt
        # testdir/test2.txt
        # "test.txt"
        # 
        # # Show quick panel with fuzzy search
        if len(self.rel_paths) > 1:
            # self.rel_paths = [f for f in self.rel_to_abs_map.items()]
            first = [ix for ix in range(len(self.rel_paths)) if self.rel_paths[ix].startswith(file_name)]
            if len(first):
                selected_index = first[0]
            else:
                selected_index = -1

            window.show_quick_panel(
                items=self.rel_paths,
                on_select=self.on_select,
                flags=0, # None, https://www.sublimetext.com/docs/api_reference.html#sublime.QuickPanelFlags
                selected_index=selected_index,
                on_highlight=self.on_highlighted,
                placeholder="Search for a file to insert"
            )
        else:
            sublime.error_message('No files found')

    def on_select(self, index):
        if index >= 0:
            rel_path = self.rel_paths[index]
            # pt = self.view.sel()[0]
            # print(pt)
            # print(rel_path)

            # self.view.insert(self.edit, pt, rel_path)
            # abs_path = self.rel_to_abs_map[rel_path]
            # self.view.window().open_file(selected_file_path)
            # self.view.run_command("replace_text", {"region": (self.expanded_region.a, self.expanded_region.b), "text": rel_path})
            self.view.run_command("insert_text", {"text": rel_path})


    def on_highlighted(self, index):
        if index >= 0:
            selected_file_path = self.rel_paths[index]
            self.view.window().open_file(selected_file_path,flags=4)

class InsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        selection = self.view.sel()[0]
        self.view.insert(edit, selection.begin(), text)
