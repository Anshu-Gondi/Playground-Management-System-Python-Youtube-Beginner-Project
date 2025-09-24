# ==============================
# School Playground Management System + Reports + PDF Export
# Tkinter + SQLite3 + Matplotlib
# ==============================

import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

# ---------------------------------
# Database Setup
# ---------------------------------
connector = sqlite3.connect('Playground.db')
cursor = connector.cursor()

connector.execute('''
CREATE TABLE IF NOT EXISTS Playground (
    EQ_NAME TEXT,
    EQ_ID TEXT PRIMARY KEY NOT NULL,
    CATEGORY TEXT,
    EQ_STATUS TEXT,
    STUDENT_ID TEXT
)
''')

# ---------------------------------
# Functions
# ---------------------------------
def issue_student():
    """Prompt student ID when issuing equipment."""
    sid = sd.askstring('Student ID', "Enter Student's ID using this equipment:")
    if not sid:
        mb.showerror('Error', 'Student ID cannot be empty!')
    else:
        return sid

def display_records():
    tree.delete(*tree.get_children())
    curr = connector.execute("SELECT * FROM Playground")
    for row in curr.fetchall():
        tree.insert('', END, values=row)

def clear_fields():
    eq_status.set('Available')
    for var in [eq_id, eq_name, category, student_id]:
        var.set('')
    eq_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    if eq_status.get() == 'In Use':
        student_id.set(issue_student())
    else:
        student_id.set('N/A')

    surety = mb.askyesno('Confirm', 'Do you want to add this equipment record?')

    if surety:
        try:
            connector.execute(
                'INSERT INTO Playground (EQ_NAME, EQ_ID, CATEGORY, EQ_STATUS, STUDENT_ID) VALUES (?, ?, ?, ?, ?)',
                (eq_name.get(), eq_id.get(), category.get(), eq_status.get(), student_id.get()))
            connector.commit()
            clear_and_display()
            mb.showinfo('Success', 'Record added successfully!')
        except sqlite3.IntegrityError:
            mb.showerror('Duplicate ID', 'This Equipment ID already exists!')

def view_record():
    if not tree.focus():
        mb.showerror('Error', 'Select a record from the table.')
        return
    values = tree.item(tree.focus())['values']
    eq_name.set(values[0])
    eq_id.set(values[1])
    category.set(values[2])
    eq_status.set(values[3])
    try:
        student_id.set(values[4])
    except:
        student_id.set('')

def update_record():
    def update():
        if eq_status.get() == 'In Use':
            student_id.set(issue_student())
        else:
            student_id.set('N/A')

        cursor.execute('UPDATE Playground SET EQ_NAME=?, CATEGORY=?, EQ_STATUS=?, STUDENT_ID=? WHERE EQ_ID=?',
                       (eq_name.get(), category.get(), eq_status.get(), student_id.get(), eq_id.get()))
        connector.commit()
        clear_and_display()
        edit_btn.destroy()
        eq_id_entry.config(state='normal')
        clear.config(state='normal')

    view_record()
    eq_id_entry.config(state='disable')
    clear.config(state='disable')
    edit_btn = Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit_btn.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror('Error', 'Select a record to delete.')
        return
    selection = tree.item(tree.focus())['values']
    cursor.execute('DELETE FROM Playground WHERE EQ_ID=?', (selection[1],))
    connector.commit()
    tree.delete(tree.focus())
    mb.showinfo('Deleted', 'Record deleted successfully!')
    clear_and_display()

def delete_inventory():
    if mb.askyesno('Confirm', 'Delete all playground records? This cannot be undone!'):
        tree.delete(*tree.get_children())
        cursor.execute('DELETE FROM Playground')
        connector.commit()

def change_status():
    if not tree.selection():
        mb.showerror('Error', 'Select a record first.')
        return
    values = tree.item(tree.focus())['values']
    EQ_id, status = values[1], values[3]

    if status == 'In Use':
        surety = mb.askyesno('Return Equipment', 'Has the equipment been returned?')
        if surety:
            cursor.execute('UPDATE Playground SET EQ_STATUS=?, STUDENT_ID=? WHERE EQ_ID=?',
                           ('Available', 'N/A', EQ_id))
            connector.commit()
    else:
        cursor.execute('UPDATE Playground SET EQ_STATUS=?, STUDENT_ID=? WHERE EQ_ID=?',
                       ('In Use', issue_student(), EQ_id))
        connector.commit()
    clear_and_display()

# ------------------------
# Report Generator with PDF Export
# ------------------------
def generate_report(pdf_export=False):
    cursor.execute("SELECT CATEGORY, COUNT(*) FROM Playground GROUP BY CATEGORY")
    category_data = cursor.fetchall()

    cursor.execute("SELECT EQ_STATUS, COUNT(*) FROM Playground GROUP BY EQ_STATUS")
    status_data = cursor.fetchall()

    if not category_data and not status_data:
        mb.showinfo("No Data", "No records available for report.")
        return

    # For PDF export
    if pdf_export:
        pdf_file = f"Playground_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = PdfPages(pdf_file)

    # Bar Chart: Category wise count
    if category_data:
        categories, counts = zip(*category_data)
        plt.figure(figsize=(6, 4))
        plt.bar(categories, counts, color='skyblue')
        plt.title("Category-wise Equipment Count")
        plt.xlabel("Category")
        plt.ylabel("Number of Equipments")
        if pdf_export:
            pdf.savefig()
        else:
            plt.show()
        plt.close()

    # Pie Chart: Available vs In Use
    if status_data:
        statuses, counts = zip(*status_data)
        plt.figure(figsize=(5, 5))
        plt.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=140, colors=['green', 'red'])
        plt.title("Equipment Status Distribution")
        if pdf_export:
            pdf.savefig()
            pdf.close()
            mb.showinfo("PDF Exported", f"Report saved as {pdf_file}")
        else:
            plt.show()
        plt.close()

# ---------------------------------
# GUI Setup
# ---------------------------------
lf_bg = '#87CEEB'
rtf_bg = '#FFD700'
rbf_bg = '#FF8C00'
btn_hlb_bg = '#90EE90'

lbl_font = ('Georgia', 13)
entry_font = ('Times New Roman', 12)
btn_font = ('Gill Sans MT', 13)

root = Tk()
root.title('School Playground Management System')
root.geometry('1400x1000')

Label(root, text="🏫 School Playground Management System 🏏",
      font=('Noto Sans CJK TC', 16, 'bold'),
      bg=btn_hlb_bg, fg='black').pack(side=TOP, fill=X)

# Variables
eq_status = StringVar()
eq_name = StringVar()
eq_id = StringVar()
category = StringVar()
student_id = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame (Inputs)
Label(left_frame, text='Equipment Name', bg=lf_bg, font=lbl_font).place(x=70, y=25)
Entry(left_frame, width=25, font=entry_font, text=eq_name).place(x=40, y=55)

Label(left_frame, text='Equipment ID', bg=lf_bg, font=lbl_font).place(x=85, y=105)
eq_id_entry = Entry(left_frame, width=25, font=entry_font, text=eq_id)
eq_id_entry.place(x=40, y=135)

Label(left_frame, text='Category (e.g. Ball, Bat, Net)', bg=lf_bg, font=lbl_font).place(x=30, y=185)
Entry(left_frame, width=25, font=entry_font, text=category).place(x=40, y=215)

Label(left_frame, text='Status', bg=lf_bg, font=lbl_font).place(x=110, y=265)
dd = OptionMenu(left_frame, eq_status, *['Available', 'In Use'])
dd.configure(font=entry_font, width=12)
dd.place(x=70, y=300)

Button(left_frame, text='Add Record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record).place(x=50, y=375)
clear = Button(left_frame, text='Clear Fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame (Actions)
Button(RT_frame, text='Delete Record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8, y=30)
Button(RT_frame, text='Delete All Records', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
Button(RT_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=17, command=update_record).place(x=348, y=30)
Button(RT_frame, text='Change Equipment Status', font=btn_font, bg=btn_hlb_bg, width=22, command=change_status).place(x=518, y=30)
Button(RT_frame, text='Generate Report 📊', font=btn_font, bg=btn_hlb_bg, width=18, command=generate_report).place(x=740, y=30)
Button(RT_frame, text='Export Report PDF 📄', font=btn_font, bg=btn_hlb_bg, width=18, command=lambda: generate_report(pdf_export=True)).place(x=348, y=80)

# Right Bottom Frame (Table)
Label(RB_frame, text='PLAYGROUND INVENTORY', bg=rbf_bg,
      font=('Noto Sans CJK TC', 15, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(RB_frame, selectmode=BROWSE,
                    columns=('Equipment Name', 'Equipment ID', 'Category', 'Status', 'Student ID'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.heading('Equipment Name', text='Equipment Name', anchor=CENTER)
tree.heading('Equipment ID', text='Equipment ID', anchor=CENTER)
tree.heading('Category', text='Category', anchor=CENTER)
tree.heading('Status', text='Status', anchor=CENTER)
tree.heading('Student ID', text='Student ID', anchor=CENTER)

tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=200, stretch=NO)
tree.column('#2', width=120, stretch=NO)
tree.column('#3', width=120, stretch=NO)
tree.column('#4', width=120, stretch=NO)
tree.column('#5', width=120, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

clear_and_display()

root.update()
root.mainloop()
