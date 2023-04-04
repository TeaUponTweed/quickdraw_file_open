import sublime
import sublime_plugin
import os


class OpenFileUnderCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the current selection
        selection = self.view.sel()[0]

        # Expand the selection to cover the whole word or file path
        self.expanded_region = self.view.expand_by_class(
            selection, sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, " ()[]\"'\t`"
        )
        file_name = self.view.substr(self.expanded_region)

        # Remove any leading/trailing whitespaces, brackets, or quotes
        file_name = file_name.strip(" '\"[]()<>\n`").rstrip(',.')

        # List all files in the project folders
        window = self.view.window()
        project_data = window.project_data() if window else None
        project_folders = (
            project_data["folders"]
            if project_data and "folders" in project_data
            else []
        )

        matching_file = None
        for directory in project_folders:
            path = directory["path"]
            for root, _, files in os.walk(path):
                if ".git/" in root:
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

        if matching_file is not None:
            self.view.window().open_file(matching_file)
        else:
            sublime.error_message("File not found: {}".format(file_name))


class FuzzyFileSplatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # List all files in the project folders
        window = self.view.window()
        project_data = window.project_data() if window else None
        project_folders = (
            project_data["folders"]
            if project_data and "folders" in project_data
            else []
        )
        self.rel_paths = []
        for directory in project_folders:
            path = directory["path"]
            for root, _, files in os.walk(path):
                if ".git/" in root:
                    continue
                for file in files:
                    abs_path = os.path.abspath(os.path.join(root, file))
                    rel_path = os.path.relpath(abs_path, path)
                    # self.rel_to_abs_map[rel_path] = abs_path
                    self.rel_paths.append(rel_path)

        # Show quick panel with fuzzy search (built-in)
        # Implementation https://www.forrestthewoods.com/blog/reverse_engineering_sublime_texts_fuzzy_match/
        if len(self.rel_paths) > 1:
            selected_index = -1
            window.show_quick_panel(
                items=self.rel_paths,
                on_select=self.on_select,
                flags=0,  # None, https://www.sublimetext.com/docs/api_reference.html#sublime.QuickPanelFlags
                selected_index=selected_index,
                on_highlight=self.on_highlighted,
                placeholder="Search for a file to insert",
            )
        else:
            sublime.error_message("No files found")

    def on_select(self, index):
        if index >= 0:
            rel_path = self.rel_paths[index]
            self.view.run_command("insert_text", {"text": rel_path})

    def on_highlighted(self, index):
        pass


class InsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        selection = self.view.sel()[0]
        self.view.insert(edit, selection.begin(), text)
