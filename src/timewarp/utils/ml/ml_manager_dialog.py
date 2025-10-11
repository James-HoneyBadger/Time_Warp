"""
ML Manager Dialog for Time_Warp IDE
GUI interface for managing machine learning models and datasets.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MLManagerDialog:
    """Machine Learning model and dataset management dialog"""

    def __init__(self, ide):
        self.ide = ide
        self.window = None

    def show(self):
        """Show the ML management dialog"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.ide.root)
        self.window.title("AI/ML Manager")
        self.window.geometry("600x500")
        self.window.transient(self.ide.root)

        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Models tab
        models_frame = ttk.Frame(notebook)
        notebook.add(models_frame, text="Models")
        self.setup_models_tab(models_frame)

        # Datasets tab
        datasets_frame = ttk.Frame(notebook)
        notebook.add(datasets_frame, text="Datasets")
        self.setup_datasets_tab(datasets_frame)

        # Quick Demo tab
        demo_frame = ttk.Frame(notebook)
        notebook.add(demo_frame, text="Quick Demo")
        self.setup_demo_tab(demo_frame)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def setup_models_tab(self, parent):
        """Setup the models management tab"""
        # Model list
        list_frame = ttk.LabelFrame(parent, text="Loaded Models")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for models
        columns = ("Name", "Type", "Status", "Trained")
        self.models_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.models_tree.heading(col, text=col)
            self.models_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.models_tree.yview
        )
        self.models_tree.configure(yscrollcommand=scrollbar.set)

        self.models_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Model controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(controls_frame, text="Load Model", command=self.load_model).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(controls_frame, text="Remove Model", command=self.remove_model).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            controls_frame, text="Model Info", command=self.show_model_info
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_models).pack(
            side=tk.LEFT, padx=2
        )

    def setup_datasets_tab(self, parent):
        """Setup the datasets management tab"""
        # Dataset list
        list_frame = ttk.LabelFrame(parent, text="Available Datasets")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for datasets
        columns = ("Name", "Type", "Size", "Features")
        self.datasets_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.datasets_tree.heading(col, text=col)
            self.datasets_tree.column(col, width=120)

        scrollbar2 = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.datasets_tree.yview
        )
        self.datasets_tree.configure(yscrollcommand=scrollbar2.set)

        self.datasets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        # Dataset controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            controls_frame, text="Create Sample Data", command=self.create_sample_data
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            controls_frame, text="Remove Dataset", command=self.remove_dataset
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="View Data", command=self.view_dataset).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_datasets).pack(
            side=tk.LEFT, padx=2
        )

    def setup_demo_tab(self, parent):
        """Setup the quick demo tab"""
        # Demo selection
        demo_frame = ttk.LabelFrame(parent, text="Educational ML Demonstrations")
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Demo buttons
        ttk.Label(
            demo_frame, text="Choose a demonstration to run:", font=("Arial", 12)
        ).pack(pady=10)

        button_frame = ttk.Frame(demo_frame)
        button_frame.pack(expand=True)

        demos = [
            (
                "Linear Regression",
                "linear",
                "Learn how linear models predict continuous values",
            ),
            (
                "Classification",
                "classification",
                "Learn how to classify data into categories",
            ),
            (
                "Clustering",
                "clustering",
                "Learn how to find patterns and group similar data",
            ),
        ]

        for i, (title, demo_type, desc) in enumerate(demos):
            frame = ttk.Frame(button_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Button(
                frame,
                text=f"Run {title} Demo",
                command=lambda dt=demo_type: self.run_demo(dt),
            ).pack(side=tk.LEFT)
            ttk.Label(frame, text=desc, foreground="gray").pack(side=tk.LEFT, padx=10)

        # Info text
        info_text = tk.Text(demo_frame, height=8, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info_text.insert(
            tk.END,
            """🤖 AI/ML Integration Help:

• Use ML: commands in PILOT language (ML:LOAD, ML:TRAIN, ML:PREDICT)
• Use MLLOAD, MLTRAIN, MLPREDICT in BASIC
• Use LOADMODEL, TRAINMODEL, PREDICT in Logo
• All demos create sample data automatically
• Check the output window to see ML results

Educational Features:
- Visual feedback for all operations
- Sample datasets for learning
- Step-by-step ML workflow
- Real-time predictions""",
        )
        info_text.config(state=tk.DISABLED)

    def load_model(self):
        """Load a new ML model"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Load Model")
        dialog.geometry("400x200")
        dialog.transient(self.window)

        ttk.Label(dialog, text="Model Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Model Type:").pack(pady=5)
        type_var = tk.StringVar(value="linear_regression")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, width=30)
        type_combo["values"] = (
            "linear_regression",
            "logistic_regression",
            "decision_tree",
            "kmeans",
        )
        type_combo.pack(pady=5)

        def do_load():
            name = name_entry.get().strip()
            model_type = type_var.get()
            if name and model_type:
                if hasattr(self.ide, "interpreter") and hasattr(
                    self.ide.interpreter, "aiml"
                ):
                    if self.ide.interpreter.aiml.load_model(name, model_type):
                        self.refresh_models()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to load model")
                else:
                    messagebox.showerror("Error", "ML integration not available")
            else:
                messagebox.showwarning(
                    "Warning", "Please enter model name and select type"
                )

        ttk.Button(dialog, text="Load", command=do_load).pack(pady=10)

    def remove_model(self):
        """Remove selected model"""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to remove")
            return

        model_name = self.models_tree.item(selection[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Remove model '{model_name}'?"):
            if (
                hasattr(self.ide, "interpreter")
                and hasattr(self.ide.interpreter, "aiml")
                and model_name in self.ide.interpreter.aiml.models
            ):
                del self.ide.interpreter.aiml.models[model_name]
                self.refresh_models()

    def show_model_info(self):
        """Show detailed model information"""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model")
            return

        model_name = self.models_tree.item(selection[0])["values"][0]
        if hasattr(self.ide, "interpreter") and hasattr(self.ide.interpreter, "aiml"):
            info = self.ide.interpreter.aiml.get_model_info(model_name)

            if info:
                info_text = f"""Model Information:

Name: {model_name}
Type: {info['type']}
Trained: {'Yes' if info['trained'] else 'No'}

Training History:
{self.ide.interpreter.aiml.training_history.get(model_name, 'No training history')}
"""
                messagebox.showinfo("Model Info", info_text)

    def refresh_models(self):
        """Refresh the models list"""
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)

        if hasattr(self.ide, "interpreter") and hasattr(self.ide.interpreter, "aiml"):
            for name, info in self.ide.interpreter.aiml.models.items():
                status = "Ready" if info["trained"] else "Not Trained"
                trained = "Yes" if info["trained"] else "No"
                self.models_tree.insert(
                    "", tk.END, values=(name, info["type"], status, trained)
                )

    def create_sample_data(self):
        """Create sample dataset"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Create Sample Data")
        dialog.geometry("400x200")
        dialog.transient(self.window)

        ttk.Label(dialog, text="Dataset Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Data Type:").pack(pady=5)
        type_var = tk.StringVar(value="linear")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, width=30)
        type_combo["values"] = ("linear", "classification", "clustering")
        type_combo.pack(pady=5)

        def do_create():
            name = name_entry.get().strip()
            data_type = type_var.get()
            if name and data_type:
                if hasattr(self.ide, "interpreter") and hasattr(
                    self.ide.interpreter, "aiml"
                ):
                    if self.ide.interpreter.aiml.create_sample_data(name, data_type):
                        self.refresh_datasets()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to create dataset")
                else:
                    messagebox.showerror("Error", "ML integration not available")
            else:
                messagebox.showwarning(
                    "Warning", "Please enter dataset name and select type"
                )

        ttk.Button(dialog, text="Create", command=do_create).pack(pady=10)

    def remove_dataset(self):
        """Remove selected dataset"""
        selection = self.datasets_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a dataset to remove")
            return

        dataset_name = self.datasets_tree.item(selection[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Remove dataset '{dataset_name}'?"):
            if (
                hasattr(self.ide, "interpreter")
                and hasattr(self.ide.interpreter, "aiml")
                and dataset_name in self.ide.interpreter.aiml.datasets
            ):
                del self.ide.interpreter.aiml.datasets[dataset_name]
                self.refresh_datasets()

    def view_dataset(self):
        """View dataset information"""
        selection = self.datasets_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a dataset")
            return

        dataset_name = self.datasets_tree.item(selection[0])["values"][0]
        if hasattr(self.ide, "interpreter") and hasattr(self.ide.interpreter, "aiml"):
            dataset = self.ide.interpreter.aiml.datasets.get(dataset_name)

            if dataset:
                info_text = f"""Dataset Information:
                
Name: {dataset_name}
Type: {dataset.get('type', 'Unknown')}
Features Shape: {dataset['X'].shape if 'X' in dataset else 'N/A'}
Targets Shape: {dataset['y'].shape if 'y' in dataset else 'N/A'}
Sample Features: {str(dataset['X'][:3]) if 'X' in dataset else 'N/A'}
"""
                messagebox.showinfo("Dataset Info", info_text)

    def refresh_datasets(self):
        """Refresh the datasets list"""
        for item in self.datasets_tree.get_children():
            self.datasets_tree.delete(item)

        if hasattr(self.ide, "interpreter") and hasattr(self.ide.interpreter, "aiml"):
            for name, data in self.ide.interpreter.aiml.datasets.items():
                data_type = data.get("type", "Unknown")
                size = f"{data['X'].shape[0]}" if "X" in data else "Unknown"
                features = (
                    f"{data['X'].shape[1]}"
                    if "X" in data and len(data["X"].shape) > 1
                    else "1"
                )
                self.datasets_tree.insert(
                    "", tk.END, values=(name, data_type, size, features)
                )

    def run_demo(self, demo_type):
        """Run ML demonstration"""
        try:
            if hasattr(self.ide, "interpreter") and hasattr(
                self.ide.interpreter, "_run_ml_demo"
            ):
                self.ide.interpreter._run_ml_demo(demo_type)
                self.refresh_models()
                self.refresh_datasets()
                messagebox.showinfo(
                    "Demo Complete",
                    f"{demo_type.title()} demonstration completed!\\nCheck the output window for results.",
                )
            else:
                messagebox.showerror("Error", "ML demo functionality not available")
        except Exception as e:
            messagebox.showerror("Demo Error", f"Error running demo: {e}")

    def close(self):
        """Close the ML manager window"""
        if self.window:
            self.window.destroy()
            self.window = None
