import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

class StrokeRiskModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.poly = PolynomialFeatures(degree=2, include_bias=False)
        self.feature_selector = SelectKBest(f_classif, k=20)
        self.model_path = 'static/models/stroke_model.keras'
        self.scaler_path = 'static/models/scaler.joblib'
        self.label_encoders_path = 'static/models/label_encoders.joblib'
        self.poly_path = 'static/models/poly.joblib'
        self.feature_selector_path = 'static/models/feature_selector.joblib'
        
        # Create models directory if it doesn't exist
        os.makedirs('static/models', exist_ok=True)
        
        # Load or train the model
        try:
            if all(os.path.exists(path) for path in [self.model_path, self.scaler_path, 
                                                   self.label_encoders_path, self.poly_path,
                                                   self.feature_selector_path]):
                self.load_model()
            else:
                print("Training new model...")
                self.train_model()
        except Exception as e:
            print(f"Error during model initialization: {str(e)}")
            raise

    def create_interaction_features(self, df):
        """Create interaction features between important variables."""
        # Age interactions
        df['age_hypertension'] = df['age'] * df['hypertension']
        df['age_heart_disease'] = df['age'] * df['heart_disease']
        df['age_glucose'] = df['age'] * df['avg_glucose_level']
        df['age_bmi'] = df['age'] * df['bmi']
        
        # Health condition interactions
        df['hypertension_heart_disease'] = df['hypertension'] * df['heart_disease']
        df['hypertension_glucose'] = df['hypertension'] * df['avg_glucose_level']
        df['heart_disease_glucose'] = df['heart_disease'] * df['avg_glucose_level']
        
        return df

    def preprocess_data(self, data):
        """
        Enhanced preprocessing with feature engineering and selection.
        """
        # Create a copy of the data
        df = data.copy()
        
        # Drop the 'id' column as it's not relevant for prediction
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
            
        # Handle missing values - using more sophisticated method
        df['bmi'] = df['bmi'].fillna(df['bmi'].mean())
        
        # Create interaction features
        df = self.create_interaction_features(df)
        
        # Define categorical columns
        categorical_columns = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
        
        # Initialize label encoders only if they don't exist
        if not self.label_encoders:
            self.label_encoders = {}
            # Fit new encoders
            for column in categorical_columns:
                self.label_encoders[column] = LabelEncoder()
                df[column] = self.label_encoders[column].fit_transform(df[column].astype(str))
        else:
            # Use existing encoders
            for column in categorical_columns:
                df[column] = self.label_encoders[column].transform(df[column].astype(str))
        
        # Convert all columns to float32
        for column in df.columns:
            df[column] = df[column].astype('float32')
        
        # Split features and target
        if 'stroke' in df.columns:
            X = df.drop('stroke', axis=1)
            y = df['stroke']
        else:
            X = df
            y = None
            
        # Apply polynomial features
        if y is not None:  # During training
            X = self.poly.fit_transform(X)
            # Select best features
            X = self.feature_selector.fit_transform(X, y)
            # Scale the features
            X = self.scaler.fit_transform(X)
        else:  # During prediction
            if not hasattr(self.scaler, 'mean_'):
                raise ValueError("Model is not trained yet. Please train the model first.")
            X = self.poly.transform(X)
            X = self.feature_selector.transform(X)
            X = self.scaler.transform(X)
            
        if y is not None:
            return X, y
        return X

    def create_model(self, input_shape):
        inputs = tf.keras.Input(shape=(input_shape,))
        
        # First block
        x = tf.keras.layers.Dense(256, activation='relu')(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.4)(x)
        
        # Second block
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        # Third block
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        
        # Fourth block
        x = tf.keras.layers.Dense(32, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.1)(x)
        
        # Output layer
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Use a more sophisticated optimizer
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        
        model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(), 
                    tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
        return model

    def train_model(self):
        try:
            # Load the dataset
            df = pd.read_csv('data/healthcare-dataset-stroke-data.csv')
            
            # Basic data validation
            required_columns = ['id', 'gender', 'age', 'hypertension', 'heart_disease', 
                              'ever_married', 'work_type', 'Residence_type', 
                              'avg_glucose_level', 'bmi', 'smoking_status', 'stroke']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in dataset: {missing_columns}")
            
            # Remove id column if exists
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            
            # Store mean BMI for future use
            self.mean_bmi = df['bmi'].mean()
            
            # Convert binary columns
            df['hypertension'] = df['hypertension'].astype(int)
            df['heart_disease'] = df['heart_disease'].astype(int)
            df['stroke'] = df['stroke'].astype(int)
            
            # Preprocess the data
            X, y = self.preprocess_data(df)
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            
            # Create and train the model
            self.model = self.create_model(X_train.shape[1])
            
            # Class weights for imbalanced dataset
            class_weights = dict(zip(
                np.unique(y_train),
                1 / np.bincount(y_train) * len(y_train) / 2
            ))
            
            # Train the model with more sophisticated callbacks
            history = self.model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                class_weight=class_weights,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        monitor='val_loss',
                        patience=10,
                        restore_best_weights=True
                    ),
                    tf.keras.callbacks.ReduceLROnPlateau(
                        monitor='val_loss',
                        factor=0.2,
                        patience=5,
                        min_lr=0.00001
                    )
                ]
            )
            
            # Evaluate the model
            test_loss, test_accuracy, test_auc, test_precision, test_recall = self.model.evaluate(X_test, y_test)
            print(f"\nTest Accuracy: {test_accuracy:.4f}")
            print(f"Test AUC: {test_auc:.4f}")
            print(f"Test Precision: {test_precision:.4f}")
            print(f"Test Recall: {test_recall:.4f}")
            
            # Save the model and preprocessing objects
            os.makedirs('static/models', exist_ok=True)
            self.model.save(self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.label_encoders, self.label_encoders_path)
            joblib.dump(self.poly, self.poly_path)
            joblib.dump(self.feature_selector, self.feature_selector_path)
            
            # Plot training history
            self.plot_training_history(history)
            
            # Plot feature importance
            self.plot_feature_importance(X, y)
            
        except Exception as e:
            print(f"Error during model training: {str(e)}")
            raise

    def plot_training_history(self, history):
        plt.figure(figsize=(12, 4))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Save the plot
        os.makedirs('static/plots', exist_ok=True)
        plt.savefig('static/plots/training_history.png')
        plt.close()

    def plot_feature_importance(self, X, y):
        # Create a simpler model for feature importance
        from sklearn.ensemble import RandomForestClassifier
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X, y)
        
        # Get feature importance
        importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Plot feature importance
        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance, x='importance', y='feature')
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.savefig('static/plots/feature_importance.png')
        plt.close()

    def load_model(self):
        self.model = tf.keras.models.load_model(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.label_encoders = joblib.load(self.label_encoders_path)
        self.poly = joblib.load(self.poly_path)
        self.feature_selector = joblib.load(self.feature_selector_path)
        
        # Load mean BMI from scaler
        self.mean_bmi = self.scaler.mean_[2]  # Assuming bmi is the third column

    def predict(self, features):
        """
        Make a prediction for the given features.
        """
        try:
            # Validate input features
            required_features = ['gender', 'age', 'hypertension', 'heart_disease', 
                               'ever_married', 'work_type', 'Residence_type', 
                               'avg_glucose_level', 'bmi', 'smoking_status']
            
            missing_features = [feat for feat in required_features if feat not in features]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")
            
            # Create a dataframe with the input features
            input_df = pd.DataFrame([features])
            
            # Convert binary features
            input_df['hypertension'] = input_df['hypertension'].astype(int)
            input_df['heart_disease'] = input_df['heart_disease'].astype(int)
            
            # Validate numerical values
            if not (0 <= float(features['age']) <= 120):
                raise ValueError("Age must be between 0 and 120")
            if not (0 <= float(features['bmi']) <= 100):
                raise ValueError("BMI must be between 0 and 100")
            if not (0 <= float(features['avg_glucose_level']) <= 1000):
                raise ValueError("Average glucose level must be between 0 and 1000")
            
            # Preprocess the input data
            input_processed = self.preprocess_data(input_df)
            
            # Get prediction probability
            risk_prob = self.model.predict(input_processed)[0][0]
            return float(risk_prob)
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            raise

# Initialize the model
stroke_model = StrokeRiskModel() 