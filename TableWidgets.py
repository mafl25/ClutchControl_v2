import tkinter as tk
import tksheet as table
import copy


class PatternTableWidget(tk.Frame):
    def __init__(self, parent, row, column):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=1, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Widget variables
        self.main_label = tk.Label(self, text="Pattern table", pady=10)

        number_of_columns = 3
        table_data = [[''] * number_of_columns]
        self.table = table.Sheet(self)
        self.table.set_sheet_data(table_data)
        self.table.enable_bindings(("single_select",
                                    "row_select",
                                    "column_width_resize",
                                    "arrowkeys",
                                    "right_click_popup_menu",
                                    "rc_select",
                                    "rc_insert_row",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"))
        self.table.hide(canvas='x_scrollbar')

        # Widget positioning
        self.main_label.grid(row=0, column=0)
        self.table.grid(row=1, column=0, padx=5)

    def get_data(self):
        original_data = copy.deepcopy(self.table.get_sheet_data())
        sanitized_data = []
        try:
            for row in original_data:
                new_row = []
                for index, element in enumerate(row):
                    try:
                        new_row.append(float(element))
                    except ValueError:
                        if (element == 'VELOCITY' and index == 1) or (element == 'TIME' and index == 0):
                            new_row.append(element)
                        else:
                            raise Exception(print('Input error in ' + self.main_label.cget("text")))
                sanitized_data.append(new_row)
            return sanitized_data
        except Exception as error_message:
            print(error_message)
            return None

    def set_data(self, data):
        self.table.set_sheet_data(copy.deepcopy(data))


class ParameterTableWidget(tk.Frame):
    def __init__(self, parent, row, column, title):
        super().__init__(parent)

        # Positioning in parent
        self.config(padx=5, pady=5)
        self.grid(row=row, column=column, columnspan=1, sticky='nsew')
        parent.columnconfigure(column, weight=1)

        # Non widget member variables
        self.randomize_variable = tk.BooleanVar()
        self.randomize_variable.set(False)

        # Widget member variables
        self.main_label = tk.Label(self, text=title, pady=10)

        self.randomize_checkbutton = tk.Checkbutton(self,
                                                    text="Randomize",
                                                    variable=self.randomize_variable)

        table_data = [['']]
        self.table = table.Sheet(self)
        self.table.set_sheet_data(table_data)
        self.table.enable_bindings(("single_select",
                                    "row_select",
                                    "column_width_resize",
                                    "arrowkeys",
                                    "right_click_popup_menu",
                                    "rc_select",
                                    "rc_insert_row",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"))

        # Widget positioning
        self.main_label.grid(row=0, column=0, sticky='w')
        self.randomize_checkbutton.grid(row=0, column=1, sticky='e')
        self.table.grid(row=1, column=0, columnspan=2, padx=5)

    def get_data(self):
        original_data = copy.deepcopy(self.table.get_sheet_data())
        sanitized_data = []
        for row in original_data:
            new_row = []
            for index, element in enumerate(row):
                try:
                    new_row.append(float(element))
                    sanitized_data.append(new_row)
                except ValueError:
                    print('Input error in ' + self.main_label.cget("text"))
        print('Sanitize data')
        print(sanitized_data)
        return sanitized_data

    def set_data(self, data):
        self.table.set_sheet_data(copy.deepcopy(data))

    def should_randomize_data(self):
        return self.randomize_variable.get()
