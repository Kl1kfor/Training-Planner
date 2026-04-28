import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import sqlite3

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Data storage
        self.trainings = []
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Добавить тренировку", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Date input
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Training type input
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=20)
        self.type_combo['values'] = ('Бег', 'Плавание', 'Велосипед', 'Силовая', 'Йога', 'Другое')
        self.type_combo.set('Бег')
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Duration input
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Filter Frame
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Filter by type
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, width=20)
        self.filter_type_combo['values'] = ('Все', 'Бег', 'Плавание', 'Велосипед', 'Силовая', 'Йога', 'Другое')
        self.filter_type_combo.set('Все')
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())
        
        # Filter by date
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date_entry.bind('<KeyRelease>', lambda e: self.refresh_table())
        
        # Clear filters button
        self.clear_filters_btn = ttk.Button(filter_frame, text="Очистить фильтры", command=self.clear_filters)
        self.clear_filters_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Table Frame
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview for displaying trainings
        columns = ('date', 'type', 'duration')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('date', text='Дата')
        self.tree.heading('type', text='Тип тренировки')
        self.tree.heading('duration', text='Длительность (мин)')
        
        # Define column widths
        self.tree.column('date', width=120)
        self.tree.column('type', width=150)
        self.tree.column('duration', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Delete button
        self.delete_button = ttk.Button(button_frame, text="Удалить выбранную тренировку", command=self.delete_training)
        self.delete_button.grid(row=0, column=0, padx=5)
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json)
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json)
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Statistics label
        self.stats_label = ttk.Label(main_frame, text="", font=('Arial', 10))
        self.stats_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def validate_date(self, date_string):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_string):
        """Validate duration is positive number"""
        try:
            duration = float(duration_string)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Add a new training record"""
        date = self.date_entry.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_entry.get().strip()
        
        # Validate inputs
        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка", "Выберите тип тренировки!")
            return
        
        if not duration:
            messagebox.showerror("Ошибка", "Введите длительность!")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Add training
        training = {
            'date': date,
            'type': training_type,
            'duration': float(duration)
        }
        self.trainings.append(training)
        
        # Sort by date
        self.trainings.sort(key=lambda x: x['date'])
        
        # Clear inputs
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.duration_entry.delete(0, tk.END)
        
        # Refresh display
        self.refresh_table()
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    def delete_training(self):
        """Delete selected training"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return
        
        # Get the item
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Find and remove from list
        for training in self.trainings:
            if (training['date'] == values[0] and 
                training['type'] == values[1] and 
                training['duration'] == float(values[2])):
                self.trainings.remove(training)
                break
        
        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def refresh_table(self):
        """Refresh the table with filters applied"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filters
        filtered_trainings = self.trainings.copy()
        
        # Filter by type
        filter_type = self.filter_type_var.get()
        if filter_type != 'Все':
            filtered_trainings = [t for t in filtered_trainings if t['type'] == filter_type]
        
        # Filter by date
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            filtered_trainings = [t for t in filtered_trainings if t['date'] == filter_date]
        
        # Add to table
        for training in filtered_trainings:
            self.tree.insert('', tk.END, values=(
                training['date'],
                training['type'],
                f"{training['duration']:.1f}"
            ))
        
        # Update statistics
        total_duration = sum(t['duration'] for t in filtered_trainings)
        avg_duration = total_duration / len(filtered_trainings) if filtered_trainings else 0
        self.stats_label.config(
            text=f"Всего тренировок: {len(filtered_trainings)} | "
                 f"Общая длительность: {total_duration:.1f} мин | "
                 f"Средняя длительность: {avg_duration:.1f} мин"
        )
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_type_var.set('Все')
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()
    
    def save_to_json(self):
        """Save data to JSON file"""
        try:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены в data.json!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_from_json(self):
        """Load data from JSON file"""
        try:
            if os.path.exists('data.json'):
                with open('data.json', 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, list):
                        self.trainings = loaded_data
                        self.refresh_table()
                        messagebox.showinfo("Успех", f"Загружено {len(loaded_data)} тренировок!")
                    else:
                        messagebox.showerror("Ошибка", "Неверный формат JSON файла!")
            else:
                messagebox.showwarning("Предупреждение", "Файл data.json не найден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def load_data(self):
        """Load initial data from JSON if exists"""
        try:
            if os.path.exists('data.json'):
                with open('data.json', 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, list):
                        self.trainings = loaded_data
        except Exception as e:
            print(f"Error loading initial data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()