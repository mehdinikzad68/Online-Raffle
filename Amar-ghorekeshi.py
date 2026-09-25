import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
import pygame

# --- بخش گرافیکی قرعه‌کشی (GUI) ---
class WinnerAnimation(tk.Toplevel):
    """
    کلاسی برای ایجاد پنجره پاپ‌آپ انیمیشنی جهت نمایش نام برنده.
    """
    def __init__(self, parent, winner_name, winner_number_text, candidate_names):
        super().__init__(parent)
        self.winner_name = winner_name
        self.winner_number_text = winner_number_text
        self.candidate_names = candidate_names
        self.alpha = 0.0
        
        self.overrideredirect(True)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.configure(bg='black')
        self.attributes('-alpha', self.alpha)
        
        self.shuffle_label = tk.Label(self, text="", font=("Arial", 100, "bold"), fg="white", bg="black")
        self.shuffle_label.pack(expand=True)
        
        self.play_sound()
        self.after(100, self.fade_in)

    def play_sound(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("draw_sound.mp3") 
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Warning: Could not play sound. Make sure 'draw_sound.mp3' is in the same folder.\nError: {e}")

    def fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.05
            self.attributes('-alpha', self.alpha)
            self.after(50, self.fade_in)
        else:
            self.after(100, self.start_shuffling)

    def start_shuffling(self, shuffle_duration=5000, interval=100):
        if not self.candidate_names:
            self.shuffle_label.config(text="Selecting...")
        else:
            random_name = random.choice(self.candidate_names)
            self.shuffle_label.config(text=random_name)
        
        if shuffle_duration > 0:
            self.after(interval, self.start_shuffling, shuffle_duration - interval, interval)
        else:
            pygame.mixer.music.stop()
            self.show_final_winner()

    def show_final_winner(self):
        final_text = f"{self.winner_number_text}\n\n{self.winner_name}"
        self.shuffle_label.config(text=final_text, fg="gold")
        self.font_size = 60
        self.zoom_in_text()

    def zoom_in_text(self):
        max_font_size = 100
        if self.font_size < max_font_size:
            self.font_size += 4
            self.shuffle_label.config(font=("Arial", self.font_size, "bold"))
            self.after(25, self.zoom_in_text)
        else:
            self.after(5000, self.close_window)

    def close_window(self):
        self.destroy()

class DrawWindow(tk.Toplevel):
    def __init__(self, parent_app, qualified_df, num_winners):
        super().__init__(parent_app.root)
        
        self.parent_app = parent_app
        self.qualified_df = qualified_df
        self.num_winners = num_winners
        self.winners_drawn = 0
        self.parent_app.winners_list = []

        self.title("Live Draw Panel")
        self.geometry("600x500")

        input_frame = tk.Frame(self, pady=10)
        input_frame.pack(fill='x')
        tk.Label(input_frame, text="Winner's Row Number:", font=("Arial", 14)).pack(side='left', padx=10)
        self.entry = tk.Entry(input_frame, font=("Arial", 14), width=10, justify='center')
        self.entry.pack(side='left')
        self.draw_button = tk.Button(input_frame, text="Select Winner!", font=("Arial", 14, "bold"),
                                     bg="#4CAF50", fg="white", command=self.process_winner)
        self.draw_button.pack(side='right', padx=20)

        list_frame = tk.Frame(self, pady=10)
        list_frame.pack(fill='both', expand=True, padx=10)
        tk.Label(list_frame, text="Selected Winners List", font=("Arial", 14, "bold")).pack()
        self.winners_listbox = tk.Listbox(list_frame, font=("Tahoma", 12))
        self.winners_listbox.pack(fill='both', expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.entry.focus_set()
        self.bind('<Return>', lambda event: self.process_winner())

    def process_winner(self):
        try:
            winner_num = int(self.entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.", parent=self)
            return

        if winner_num not in self.qualified_df.index:
            messagebox.showwarning("Warning", "The entered number is not in the qualified list.", parent=self)
            return

        if any(d['Row_Number_in_List'] == winner_num for d in self.parent_app.winners_list):
            messagebox.showwarning("Duplicate", "This number has already been selected as a winner.", parent=self)
            return

        winner_info = self.qualified_df.loc[winner_num]
        winner_name = winner_info.get('نام و نام خانوادگی', 'N/A')
        candidate_names = list(self.qualified_df['نام و نام خانوادگی'])
        
        self.withdraw()
        animation_window = WinnerAnimation(self, winner_name, f"Winner #{self.winners_drawn + 1}", candidate_names)
        self.wait_window(animation_window)
        self.deiconify()
        self.entry.delete(0, 'end')
        self.entry.focus_set()

        self.winners_drawn += 1
        winner_data = {
            'Draw_Order': self.winners_drawn, 'Row_Number_in_List': winner_num,
            'Name': winner_name, 'Contact': winner_info.get('شماره تماس', 'N/A'),
            'Email': winner_info.get('ایمیل', 'N/A'), 'Score': winner_info['امتیاز']
        }
        self.parent_app.winners_list.append(winner_data)
        
        list_entry = f"{self.winners_drawn}. {winner_name} (Row #{winner_num})"
        self.winners_listbox.insert('end', list_entry)

        if self.winners_drawn >= self.num_winners:
            messagebox.showinfo("Draw Complete", f"The draw for {self.num_winners} winners is complete.", parent=self)
            self.draw_button.config(state='disabled', text="Draw Finished")

    def on_closing(self):
        if self.parent_app.winners_list:
            self.parent_app.save_winners_list()
        self.destroy()

# --- کلاس اصلی برنامه ---
class QuizSystem:
    def __init__(self, root):
        self.root = root
        self.file_path = self.select_input_file()
        if not self.file_path:
            self.df = None
            return

        self.df = None
        self.qualified_df = None
        self.stats = {}
        self.winners_list = []
        self.load_and_analyze_data()

    def select_input_file(self):
        messagebox.showinfo("Select File", "Please select the Excel file containing the quiz results.", parent=self.root)
        file_path = filedialog.askopenfilename(
            title="Select Quiz Results Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            print("❌ No file selected. Exiting program.")
            self.root.destroy()
            return None
        return file_path

    def load_and_analyze_data(self):
        try:
            self.df = pd.read_excel(self.file_path)
            correct_answers = {
                'سوال 1': 'گزینه صحیح سوال 1',
                'سوال 2': 'گزینه صحیح سوال 2',
                'سوال 3': 'گزینه صحیح سوال 3'
            }
            def calculate_score(row):
                score = 0
                for q, a in correct_answers.items():
                    if q in row and str(row.get(q, '')).strip() == str(a).strip():
                        score += 1
                return score
            
            self.df['امتیاز'] = self.df.apply(calculate_score, axis=1)
            self.df = self.df.sort_values(by='امتیاز', ascending=False).reset_index(drop=True)
            self.qualified_df = self.df[self.df['امتیاز'] >= 2].reset_index(drop=True)
            self.qualified_df.index += 1
            
            self.stats = {
                'Total Participants': len(self.df), '3 Correct Answers': len(self.df[self.df['امتیاز'] == 3]),
                '2 Correct Answers': len(self.df[self.df['امتیاز'] == 2]), '1 Correct Answer': len(self.df[self.df['امتیاز'] == 1]),
                '0 Correct Answers': len(self.df[self.df['امتیاز'] == 0]), 'Total Qualified for Draw': len(self.qualified_df)
            }
            print("✅ Excel file loaded and analyzed successfully.")
        except Exception as e:
            print(f"❌ An error occurred while loading or analyzing the file: {e}")
            self.df = None

    def main_menu(self):
        while True:
            print("\n" + "="*45)
            print("   Main Menu - Conference Quiz System   ")
            print("="*45)
            print("1. Display Overall Statistics")
            print("2. Display & Save List of Qualified Participants")
            print("3. Export Advanced Excel Report")
            print("4. Display Graphical Charts")
            print("5. Start Live Draw Process")
            print("0. Exit Program")
            print("="*45)
            
            choice = input("Please select an option: ")
            
            if choice == '1': self.show_stats()
            elif choice == '2': self.show_and_save_qualified_list()
            elif choice == '3': self.export_to_excel()
            elif choice == '4': self.show_charts()
            elif choice == '5': self.start_draw_process()
            elif choice == '0':
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")

    def show_stats(self):
        print("\n--- Overall Quiz Statistics ---")
        for key, value in self.stats.items():
            print(f"{key}: {value}")
        input("\nPress Enter to return to the main menu...")

    def show_and_save_qualified_list(self):
        print("\n--- List of Participants Qualified for the Draw ---")
        if not self.qualified_df.empty:
            columns_to_show = ['نام و نام خانوادگی', 'شماره تماس', 'ایمیل', 'امتیاز']
            existing_cols = [col for col in columns_to_show if col in self.qualified_df.columns]
            print(self.qualified_df[existing_cols])
            
            print("-" * 45)
            save_choice = messagebox.askyesno(
                "Save Qualified List", 
                "The list of qualified participants is displayed in the console.\n\nWould you like to save this list to an Excel file?",
                parent=self.root
            )
            
            if save_choice:
                save_path = filedialog.asksaveasfilename(
                    title="Save Qualified List As...",
                    defaultextension=".xlsx",
                    filetypes=[("Excel Files", "*.xlsx")],
                    initialfile="Qualified_Participants_List.xlsx",
                    parent=self.root
                )
                if save_path:
                    try:
                        self.qualified_df[existing_cols].to_excel(save_path, index=True, index_label='ردیف')
                        print(f"\n✅ Qualified list saved successfully to '{save_path}'.")
                    except Exception as e:
                        print(f"\n❌ An error occurred while saving the qualified list file: {e}")
                else:
                    print("\n❌ Save operation cancelled.")
            else:
                print("\nℹ️ The list was not saved to a file.")
                
        else:
            print("No participants are qualified for the draw.")
        
        input("\nPress Enter to return to the main menu...")

    def export_to_excel(self):
        save_path = filedialog.asksaveasfilename(
            title="Save Excel Report As...",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="Quiz_Report_Advanced.xlsx",
            parent=self.root
        )
        if not save_path:
            print("❌ Save operation cancelled.")
            input("\nPress Enter to return to the main menu...")
            return

        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                stats_df = pd.DataFrame(list(self.stats.items()), columns=['Statistic', 'Value'])
                stats_df.to_excel(writer, sheet_name='Dashboard', index=False)
                
                self.df.to_excel(writer, sheet_name='Full_Results', index=False)
                
                if not self.qualified_df.empty:
                    columns_to_show = ['نام و نام خانوادگی', 'شماره تماس', 'ایمیل', 'امتیاز']
                    existing_cols = [col for col in columns_to_show if col in self.qualified_df.columns]
                    self.qualified_df[existing_cols].to_excel(writer, sheet_name='Qualified_List', index=True, index_label='ردیف')

            print(f"✅ Advanced Excel report saved successfully to '{save_path}'.")
        except Exception as e:
            print(f"❌ An error occurred while saving the Excel file: {e}")
        
        input("\nPress Enter to return to the main menu...")

    def show_charts(self):
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.family'] = 'Tahoma'
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        pie_data = [self.stats['3 Correct Answers'], self.stats['2 Correct Answers'], self.stats['1 Correct Answer'], self.stats['0 Correct Answers']]
        pie_labels = ['3 Correct', '2 Correct', '1 Correct', '0 Correct']
        ax1.pie(pie_data, labels=pie_labels, autopct='%.1f%%', startangle=90, shadow=True, explode=(0.1, 0, 0, 0))
        ax1.set_title('Score Distribution')
        bar_data = [self.stats['Total Qualified for Draw'], self.stats['Total Participants'] - self.stats['Total Qualified for Draw']]
        bar_labels = ['Qualified', 'Not Qualified']
        ax2.bar(bar_labels, bar_data, color=['#4CAF50', '#F44336'])
        ax2.set_title('Draw Qualification Status')
        print("Displaying charts... Please close the chart window to return to the menu.")
        plt.show()

    def start_draw_process(self):
        if self.qualified_df.empty:
            messagebox.showerror("Error", "No participants are qualified for the draw.", parent=self.root)
            return

        num_winners = simpledialog.askinteger("Number of Winners", "How many winners would you like to draw?", parent=self.root, minvalue=1, maxvalue=self.stats['Total Qualified for Draw'])
        if not num_winners:
            print("❌ Draw process cancelled.")
            return

        draw_app = DrawWindow(self, self.qualified_df, num_winners)
        
        print("Live Draw Panel is open. Please proceed with the draw using the graphical window...")
        self.root.wait_window(draw_app)
        
        print("\n✅ Draw process finished in the graphical window.")
        input("Press Enter to return to the main menu...")

    def save_winners_list(self):
        if not self.winners_list: return
        save_choice = messagebox.askyesno("Save Winners", "Would you like to save the list of winners to an Excel file?", parent=self.root)
        if save_choice:
            save_path = filedialog.asksaveasfilename(
                title="Save Winners List As...", defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")], initialfile="Winners_List.xlsx", parent=self.root
            )
            if save_path:
                try:
                    winners_df = pd.DataFrame(self.winners_list)
                    winners_df.to_excel(save_path, index=False)
                    print(f"✅ Winners list saved successfully to '{save_path}'.")
                except Exception as e:
                    print(f"❌ An error occurred while saving the winners list: {e}")
            else:
                print("❌ Save operation for winners list cancelled.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    app = QuizSystem(root)
    
    if app.df is not None:
        app.main_menu()
    
    # اطمینان از بسته شدن کامل برنامه پس از خروج از منو
    # در برخی سیستم‌عامل‌ها، این کار برای خاتمه کامل فرآیندهای tkinter لازم است.
    if 'normal' == root.state():
        root.destroy()