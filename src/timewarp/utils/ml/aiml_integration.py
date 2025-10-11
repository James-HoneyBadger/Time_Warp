"""
AI/ML Integration for Time_Warp
Educational machine learning integration with scikit-learn, numpy, and pandas.
"""

from datetime import datetime


class AIMLIntegration:
    """Educational AI/ML integration for Time_Warp"""

    def __init__(self):
        self.models = {}  # name -> model_info
        self.datasets = {}  # name -> data
        self.last_prediction = None
        self.training_history = {}
        self.ml_output_callback = None

        # Try to import optional ML libraries
        self.sklearn_available = False
        self.numpy_available = False
        self.pandas_available = False

        try:
            import numpy as np

            self.np = np
            self.numpy_available = True
        except ImportError:
            self.np = None

        try:
            import pandas as pd

            self.pd = pd
            self.pandas_available = True
        except ImportError:
            # Pandas not available or failed to import
            self.pd = None
            self.pandas_available = False

        try:
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, mean_squared_error

            self.LinearRegression = LinearRegression
            self.LogisticRegression = LogisticRegression
            self.DecisionTreeClassifier = DecisionTreeClassifier
            self.KMeans = KMeans
            self.StandardScaler = StandardScaler
            self.train_test_split = train_test_split
            self.accuracy_score = accuracy_score
            self.mean_squared_error = mean_squared_error
            self.sklearn_available = True

        except ImportError:
            self.sklearn_available = False

        self.log_ml_message("AI/ML Integration initialized")
        if not self.sklearn_available:
            self.log_ml_message(
                "⚠️ scikit-learn not available - install with: pip install scikit-learn"
            )
        if not self.numpy_available:
            self.log_ml_message(
                "⚠️ numpy not available - install with: pip install numpy"
            )
        if not self.pandas_available:
            self.log_ml_message(
                "⚠️ pandas not available - install with: pip install pandas"
            )

    def set_output_callback(self, callback):
        """Set callback for ML output messages"""
        self.ml_output_callback = callback

    def log_ml_message(self, message):
        """Log ML-related messages"""
        if self.ml_output_callback:
            self.ml_output_callback(f"🤖 ML: {message}")
        else:
            print(f"🤖 ML: {message}")

    def create_sample_data(self, dataset_name, data_type="linear"):
        """Create sample datasets for educational purposes"""
        if not self.numpy_available:
            self.log_ml_message("NumPy required for sample data generation")
            return False

        try:
            if data_type == "linear":
                # Linear regression sample data
                X = self.np.linspace(0, 10, 50).reshape(-1, 1)
                y = 2 * X.flatten() + 1 + self.np.random.normal(0, 1, 50)
                self.datasets[dataset_name] = {"X": X, "y": y, "type": "regression"}

            elif data_type == "classification":
                # Simple classification data
                self.np.random.seed(42)
                X = self.np.random.randn(100, 2)
                y = (X[:, 0] + X[:, 1] > 0).astype(int)
                self.datasets[dataset_name] = {"X": X, "y": y, "type": "classification"}

            elif data_type == "clustering":
                # Clustering sample data
                self.np.random.seed(42)
                X = self.np.random.randn(100, 2)
                X[:50] += [2, 2]  # Create two clusters
                self.datasets[dataset_name] = {"X": X, "type": "clustering"}

            self.log_ml_message(
                f"Sample dataset '{dataset_name}' created ({data_type})"
            )
            return True

        except Exception as e:
            self.log_ml_message(f"Error creating sample data: {e}")
            return False

    def load_model(self, model_name, model_type="linear_regression"):
        """Load/create a machine learning model"""
        if not self.sklearn_available:
            self.log_ml_message("scikit-learn required for model operations")
            return False

        try:
            if model_type == "linear_regression":
                model = self.LinearRegression()
            elif model_type == "logistic_regression":
                model = self.LogisticRegression()
            elif model_type == "decision_tree":
                model = self.DecisionTreeClassifier(random_state=42)
            elif model_type == "kmeans":
                model = self.KMeans(n_clusters=2, random_state=42)
            else:
                self.log_ml_message(f"Unknown model type: {model_type}")
                return False

            self.models[model_name] = {
                "model": model,
                "type": model_type,
                "trained": False,
                "features": None,
                "target": None,
            }

            self.log_ml_message(f"Model '{model_name}' ({model_type}) loaded")
            return True

        except Exception as e:
            self.log_ml_message(f"Error loading model: {e}")
            return False

    def train_model(self, model_name, dataset_name):
        """Train a model with a dataset"""
        if model_name not in self.models:
            self.log_ml_message(f"Model '{model_name}' not found")
            return False

        if dataset_name not in self.datasets:
            self.log_ml_message(f"Dataset '{dataset_name}' not found")
            return False

        try:
            model_info = self.models[model_name]
            dataset = self.datasets[dataset_name]

            if model_info["type"] == "kmeans":
                # Clustering doesn't need target variable
                model_info["model"].fit(dataset["X"])
            else:
                # Supervised learning
                if "y" not in dataset:
                    self.log_ml_message(
                        f"Dataset '{dataset_name}' missing target variable"
                    )
                    return False

                model_info["model"].fit(dataset["X"], dataset["y"])

            model_info["trained"] = True
            self.training_history[model_name] = {
                "dataset": dataset_name,
                "timestamp": datetime.now().isoformat(),
            }

            self.log_ml_message(
                f"Model '{model_name}' trained on dataset '{dataset_name}'"
            )
            return True

        except Exception as e:
            self.log_ml_message(f"Error training model: {e}")
            return False

    def predict(self, model_name, input_data):
        """Make predictions with a trained model"""
        if model_name not in self.models:
            self.log_ml_message(f"Model '{model_name}' not found")
            return None

        model_info = self.models[model_name]
        if not model_info["trained"]:
            self.log_ml_message(f"Model '{model_name}' is not trained")
            return None

        try:
            # Parse input data
            if isinstance(input_data, str):
                # Parse comma-separated values
                values = [float(x.strip()) for x in input_data.split(",")]
                input_array = self.np.array(values).reshape(1, -1)
            elif isinstance(input_data, (list, tuple)):
                input_array = self.np.array(input_data).reshape(1, -1)
            else:
                input_array = input_data

            prediction = model_info["model"].predict(input_array)
            self.last_prediction = prediction

            if model_info["type"] == "kmeans":
                self.log_ml_message(f"Cluster prediction: {prediction[0]}")
            else:
                self.log_ml_message(f"Prediction: {prediction[0]:.4f}")

            return prediction[0]

        except Exception as e:
            self.log_ml_message(f"Error making prediction: {e}")
            return None

    def evaluate_model(self, model_name, dataset_name):
        """Evaluate model performance"""
        if model_name not in self.models or dataset_name not in self.datasets:
            self.log_ml_message("Model or dataset not found")
            return None

        try:
            model_info = self.models[model_name]
            dataset = self.datasets[dataset_name]

            if not model_info["trained"]:
                self.log_ml_message(f"Model '{model_name}' is not trained")
                return None

            if model_info["type"] == "kmeans":
                # For clustering, show inertia
                score = model_info["model"].inertia_
                self.log_ml_message(f"Model inertia: {score:.4f}")
                return score
            else:
                # For supervised learning, calculate accuracy/MSE
                predictions = model_info["model"].predict(dataset["X"])

                if dataset["type"] == "classification":
                    score = self.accuracy_score(dataset["y"], predictions)
                    self.log_ml_message(f"Model accuracy: {score:.4f}")
                else:
                    score = self.mean_squared_error(dataset["y"], predictions)
                    self.log_ml_message(f"Model MSE: {score:.4f}")

                return score

        except Exception as e:
            self.log_ml_message(f"Error evaluating model: {e}")
            return None

    def list_models(self):
        """List all loaded models"""
        if not self.models:
            self.log_ml_message("No models loaded")
            return

        self.log_ml_message("Loaded models:")
        for name, info in self.models.items():
            status = "trained" if info["trained"] else "not trained"
            self.log_ml_message(f"  {name}: {info['type']} ({status})")

    def list_datasets(self):
        """List all available datasets"""
        if not self.datasets:
            self.log_ml_message("No datasets available")
            return

        self.log_ml_message("Available datasets:")
        for name, info in self.datasets.items():
            data_type = info.get("type", "unknown")
            shape = f"{info['X'].shape}" if "X" in info else "unknown shape"
            self.log_ml_message(f"  {name}: {data_type} {shape}")

    def get_model_info(self, model_name):
        """Get detailed information about a model"""
        if model_name not in self.models:
            return None

        info = self.models[model_name].copy()
        # Remove the actual model object for serialization
        info.pop("model", None)
        return info

    def clear_models(self):
        """Clear all models and datasets"""
        self.models.clear()
        self.datasets.clear()
        self.training_history.clear()
        self.log_ml_message("All models and datasets cleared")
