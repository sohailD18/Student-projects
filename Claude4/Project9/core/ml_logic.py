"""
ML Logic for AgriSense - Crop Recommendation and Fertilizer Advisory System.
Uses both rule-based logic and Decision Tree classifier for recommendations.
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler


class CropRecommender:
    """
    AI-based crop recommendation system using Decision Tree Classifier.
    """

    def __init__(self):
        """Initialize the recommender with trained model."""
        self.model = None
        self.scaler = StandardScaler()
        self.crop_labels = [
            'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane',
            'Millet', 'Barley', 'Groundnut', 'Soybean', 'Tomato',
            'Potato', 'Onion', 'Coffee', 'Tea', 'Rubber'
        ]
        self._train_model()

    def _generate_training_data(self):
        """
        Generate synthetic training data for crop recommendations.
        Based on agricultural research and soil science principles.
        """
        # Generate synthetic data based on crop requirements
        np.random.seed(42)
        n_samples = 3000

        data = []
        labels = []

        # Crop requirements: (N_range, P_range, K_range, pH_range, moisture_range, count)
        crop_requirements = [
            # (N_min, N_max, P_min, P_max, K_min, K_max, pH_min, pH_max, moist_min, moist_max, crop_name)
            (40, 80, 20, 50, 30, 60, 5.5, 7.0, 60, 100, 0),  # Rice - likes water, high N
            (50, 90, 20, 40, 20, 50, 6.0, 7.5, 40, 70, 1),    # Wheat
            (60, 100, 25, 50, 30, 70, 5.8, 7.2, 50, 80, 2),  # Maize - high nutrients
            (40, 70, 30, 60, 40, 80, 6.0, 8.0, 40, 65, 3),  # Cotton
            (30, 60, 20, 40, 30, 50, 6.5, 7.5, 50, 85, 4),  # Sugarcane
            (20, 50, 15, 35, 20, 40, 6.0, 8.0, 30, 60, 5),  # Millet - drought resistant
            (30, 60, 20, 45, 25, 50, 6.0, 7.0, 35, 65, 6),  # Barley
            (25, 55, 25, 50, 30, 60, 5.5, 7.0, 40, 70, 7),  # Groundnut
            (30, 70, 25, 55, 25, 55, 6.0, 7.5, 45, 75, 8),  # Soybean
            (50, 90, 30, 60, 40, 80, 6.0, 7.0, 50, 80, 9),  # Tomato
            (40, 80, 30, 60, 50, 90, 5.5, 6.5, 60, 85, 10), # Potato - high K
            (40, 70, 40, 70, 40, 70, 6.0, 7.0, 45, 75, 11), # Onion
            (30, 60, 20, 40, 30, 50, 5.0, 6.0, 60, 90, 12), # Coffee - acidic soil
            (40, 70, 20, 40, 30, 50, 4.5, 5.5, 65, 95, 13), # Tea - acidic, high moisture
            (25, 50, 20, 40, 30, 60, 5.0, 6.5, 55, 85, 14), # Rubber
        ]

        samples_per_crop = n_samples // len(crop_requirements)

        for req in crop_requirements:
            n_min, n_max, p_min, p_max, k_min, k_max, ph_min, ph_max, moist_min, moist_max, crop_idx = req

            for _ in range(samples_per_crop):
                # Generate random values within ranges with some variation
                n = np.random.randint(n_min, n_max + 1)
                p = np.random.randint(p_min, p_max + 1)
                k = np.random.randint(k_min, k_max + 1)
                ph = np.random.uniform(ph_min, ph_max)
                moisture = np.random.uniform(moist_min, moist_max)

                # Add some noise to make it more realistic
                if np.random.random() > 0.7:
                    n += np.random.randint(-10, 11)
                    p += np.random.randint(-8, 9)
                    k += np.random.randint(-8, 9)
                    ph += np.random.uniform(-0.5, 0.5)
                    moisture += np.random.uniform(-10, 10)

                # Clip values to reasonable ranges
                n = max(0, min(120, n))
                p = max(0, min(100, p))
                k = max(0, min(120, k))
                ph = max(0, min(14, ph))
                moisture = max(0, min(100, moisture))

                data.append([n, p, k, ph, moisture])
                labels.append(crop_idx)

        return np.array(data), np.array(labels)

    def _train_model(self):
        """Train the Decision Tree classifier."""
        X, y = self._generate_training_data()

        # Normalize features
        X_scaled = self.scaler.fit_transform(X)

        # Train Decision Tree
        self.model = DecisionTreeClassifier(
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.model.fit(X_scaled, y)

    def predict(self, nitrogen, phosphorus, potassium, ph, moisture):
        """
        Predict the best crop based on soil parameters.

        Args:
            nitrogen: Nitrogen level (0-120)
            phosphorus: Phosphorus level (0-100)
            potassium: Potassium level (0-120)
            ph: Soil pH level (0-14)
            moisture: Soil moisture percentage (0-100)

        Returns:
            str: Recommended crop name
        """
        # Prepare input features
        features = np.array([[nitrogen, phosphorus, potassium, ph, moisture]])
        features_scaled = self.scaler.transform(features)

        # Predict
        prediction = self.model.predict(features_scaled)[0]

        return self.crop_labels[prediction]


class FertilizerAdvisor:
    """
    Rule-based fertilizer recommendation system.
    """

    # Nutrient threshold definitions
    N_LOW = 40
    N_MEDIUM = 70

    P_LOW = 20
    P_MEDIUM = 40

    K_LOW = 30
    K_MEDIUM = 60

    @staticmethod
    def get_n_status(n):
        """Get nitrogen status category."""
        if n < FertilizerAdvisor.N_LOW:
            return "low"
        elif n < FertilizerAdvisor.N_MEDIUM:
            return "medium"
        else:
            return "high"

    @staticmethod
    def get_p_status(p):
        """Get phosphorus status category."""
        if p < FertilizerAdvisor.P_LOW:
            return "low"
        elif p < FertilizerAdvisor.P_MEDIUM:
            return "medium"
        else:
            return "high"

    @staticmethod
    def get_k_status(k):
        """Get potassium status category."""
        if k < FertilizerAdvisor.K_LOW:
            return "low"
        elif k < FertilizerAdvisor.K_MEDIUM:
            return "medium"
        else:
            return "high"

    @staticmethod
    def suggest_fertilizer(n, p, k, crop):
        """
        Generate fertilizer recommendations based on nutrient levels.

        Args:
            n: Nitrogen level
            p: Phosphorus level
            k: Potassium level
            crop: Recommended crop name

        Returns:
            str: Detailed fertilizer suggestions
        """
        suggestions = []

        # Get nutrient statuses
        n_status = FertilizerAdvisor.get_n_status(n)
        p_status = FertilizerAdvisor.get_p_status(p)
        k_status = FertilizerAdvisor.get_k_status(k)

        # Nitrogen recommendations
        if n_status == "low":
            suggestions.append(
                "🌱 **Nitrogen is LOW**: Apply Urea (45-50 kg/acre) or "
                "Ammonium Sulfate. Consider leguminous green manure."
            )
        elif n_status == "medium":
            suggestions.append(
                "🌱 **Nitrogen is MODERATE**: Apply Urea (25-30 kg/acre) or "
                "compost to maintain levels."
            )
        else:
            suggestions.append(
                "✅ **Nitrogen is GOOD**: Maintain with organic matter or "
                "reduced N fertilizer (10-15 kg/acre)."
            )

        # Phosphorus recommendations
        if p_status == "low":
            suggestions.append(
                "💧 **Phosphorus is LOW**: Apply Single Super Phosphate (SSP) "
                "or DAP (50-60 kg/acre). Rock phosphate is organic alternative."
            )
        elif p_status == "medium":
            suggestions.append(
                "💧 **Phosphorus is MODERATE**: Apply SSP or DAP "
                "(25-35 kg/acre) for maintenance."
            )
        else:
            suggestions.append(
                "✅ **Phosphorus is GOOD**: No immediate application needed. "
                "Monitor soil test annually."
            )

        # Potassium recommendations
        if k_status == "low":
            suggestions.append(
                "🌿 **Potassium is LOW**: Apply Muriate of Potash (MOP) "
                "(30-40 kg/acre) or wood ash."
            )
        elif k_status == "medium":
            suggestions.append(
                "🌿 **Potassium is MODERATE**: Apply MOP or potassium sulfate "
                "(15-20 kg/acre) for best results."
            )
        else:
            suggestions.append(
                "✅ **Potassium is GOOD**: Current levels are adequate. "
                "Regular monitoring recommended."
            )

        # pH-specific recommendations
        suggestions.append(
            f"\n📊 **Soil Analysis Summary:**\n"
            f"• Nitrogen (N): {n} mg/kg - {n_status.upper()}\n"
            f"• Phosphorus (P): {p} mg/kg - {p_status.upper()}\n"
            f"• Potassium (K): {k} mg/kg - {k_status.upper()}"
        )

        # Crop-specific advice
        crop_advice = FertilizerAdvisor._get_crop_specific_advice(crop, n_status, p_status, k_status)
        if crop_advice:
            suggestions.append(f"\n🎯 **Crop-Specific Advice for {crop}:**\n{crop_advice}")

        return "\n\n".join(suggestions)

    @staticmethod
    def _get_crop_specific_advice(crop, n_status, p_status, k_status):
        """Get crop-specific fertilizer recommendations."""
        advice_map = {
            'Rice': "Rice requires high nitrogen. Split N application: 50% at planting, "
                   "25% at tillering, 25% at panicle initiation.",
            'Wheat': "Wheat needs moderate N. Apply all P and K at sowing. "
                    "Split N: 50% at sowing, 50% at first irrigation.",
            'Maize': "Maize is a heavy feeder. Apply full P and K at planting. "
                    "Split N into 3 equal doses at V6, V12, and tasseling stages.",
            'Cotton': "Cotton needs balanced nutrients. Apply P and K at planting. "
                     "N should be split: at planting, square formation, and boll development.",
            'Sugarcane': "Sugarcane needs sustained nutrition. Apply 25% N at planting, "
                        "75% in 3 equal splits at 2, 4, and 6 months.",
            'Millet': "Millets are drought-resistant and need less fertilizer. "
                     "Apply 50% of recommended N, full P and K at sowing.",
            'Groundnut': "Groundnut fixes nitrogen. Avoid excess N. "
                        "Ensure adequate calcium through gypsum.",
            'Soybean': "Soybean is a nitrogen-fixing legume. Apply only 20-30 kg N/acre "
                      "as starter. Ensure adequate P and K.",
            'Tomato': "Tomatoes need high potassium for fruit quality. "
                     "Apply N, P, K in 1:2:2 ratio throughout the season.",
            'Potato': "Potatoes are potassium-loving. Apply N:P:K in 2:1:3 ratio. "
                     "Ensure adequate K for tuber development.",
        }

        return advice_map.get(crop, "Follow standard fertilizer practices for this crop. "
                                   "Consult local agricultural extension for specific guidance.")


# Initialize global recommender instance
crop_recommender = CropRecommender()


def recommend_crop(n, p, k, ph, moisture):
    """
    Main function to recommend crop based on soil parameters.

    Args:
        n: Nitrogen level
        p: Phosphorus level
        k: Potassium level
        ph: Soil pH level
        moisture: Soil moisture percentage

    Returns:
        str: Recommended crop name
    """
    return crop_recommender.predict(n, p, k, ph, moisture)


def suggest_fertilizer(n, p, k, crop):
    """
    Main function to suggest fertilizers based on nutrient levels.

    Args:
        n: Nitrogen level
        p: Phosphorus level
        k: Potassium level
        crop: Recommended crop name

    Returns:
        str: Detailed fertilizer suggestions
    """
    return FertilizerAdvisor.suggest_fertilizer(n, p, k, crop)
