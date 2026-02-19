"""
AI Analysis Module for Driver Behavior Classification

This module implements risk scoring and behavior classification algorithms
based on driving metrics such as speed, braking events, acceleration patterns,
and cornering speeds.
"""


def calculate_risk_score(
    average_speed: float,
    max_speed: float,
    harsh_braking_events: int,
    rapid_acceleration_events: int,
    cornering_speed: float,
) -> float:
    """
    Calculate a risk score (0-100) based on driving metrics.

    Scoring Algorithm:
    - Speed Score: (0-35 points) Based on max_speed and average_speed
    - Braking Score: (0-25 points) Based on harsh braking events
    - Acceleration Score: (0-25 points) Based on rapid acceleration events
    - Cornering Score: (0-15 points) Based on cornering speed

    Args:
        average_speed: Average speed during trip (km/h)
        max_speed: Maximum speed reached (km/h)
        harsh_braking_events: Count of harsh braking incidents
        rapid_acceleration_events: Count of rapid acceleration incidents
        cornering_speed: Average cornering speed (km/h)

    Returns:
        Risk score between 0 and 100 (higher = more risky)
    """
    risk_score = 0.0

    # Speed Risk Calculation (0-35 points)
    # Base speed risk from max_speed
    if max_speed > 140:
        speed_risk = 35
    elif max_speed > 120:
        speed_risk = 28
    elif max_speed > 100:
        speed_risk = 20
    elif max_speed > 80:
        speed_risk = 10
    else:
        speed_risk = 0

    # Additional risk from high average speed
    if average_speed > 100:
        speed_risk += 10
    elif average_speed > 80:
        speed_risk += 5

    risk_score += min(speed_risk, 35)

    # Braking Risk Calculation (0-25 points)
    # Each harsh braking event adds risk
    braking_risk = min(harsh_braking_events * 5, 25)
    risk_score += braking_risk

    # Acceleration Risk Calculation (0-25 points)
    # Each rapid acceleration event adds risk
    acceleration_risk = min(rapid_acceleration_events * 5, 25)
    risk_score += acceleration_risk

    # Cornering Risk Calculation (0-15 points)
    if cornering_speed > 80:
        cornering_risk = 15
    elif cornering_speed > 60:
        cornering_risk = 10
    elif cornering_speed > 40:
        cornering_risk = 5
    else:
        cornering_risk = 0
    risk_score += cornering_risk

    # Ensure score is between 0-100
    return round(min(max(risk_score, 0), 100), 2)


def classify_behavior(risk_score: float) -> str:
    """
    Classify driver behavior based on risk score.

    Classification Rules:
    - Safe: Risk score < 30
    - Moderate: Risk score between 30 and 70
    - Risky: Risk score > 70

    Args:
        risk_score: Calculated risk score (0-100)

    Returns:
        Behavior class: 'Safe', 'Moderate', or 'Risky'
    """
    if risk_score < 30:
        return 'Safe'
    elif risk_score < 70:
        return 'Moderate'
    else:
        return 'Risky'


def generate_recommendations(
    average_speed: float,
    max_speed: float,
    harsh_braking_events: int,
    rapid_acceleration_events: int,
    cornering_speed: float,
    risk_score: float,
    behavior_class: str,
) -> str:
    """
    Generate personalized safety recommendations based on driving metrics.

    Analyzes the weakest metrics and provides targeted suggestions
    to improve driving safety.

    Args:
        average_speed: Average speed during trip (km/h)
        max_speed: Maximum speed reached (km/h)
        harsh_braking_events: Count of harsh braking incidents
        rapid_acceleration_events: Count of rapid acceleration incidents
        cornering_speed: Average cornering speed (km/h)
        risk_score: Calculated risk score (0-100)
        behavior_class: Classified behavior category

    Returns:
        Formatted recommendations string
    """
    recommendations = []

    # Speed-related recommendations
    if max_speed > 120:
        recommendations.append(
            "⚠️ HIGH SPEED ALERT: Reduce maximum speed. "
            "Speeding significantly increases accident risk and stopping distance."
        )
    elif average_speed > 80:
        recommendations.append(
            "📌 MODERATE SPEED: Consider reducing average speed, "
            "especially in residential areas (recommended: <50 km/h)"
        )

    # Braking-related recommendations
    if harsh_braking_events >= 4:
        recommendations.append(
            "🛑 HARSH BRAKING: You had {} harsh braking events. "
            "Maintain longer following distance and anticipate traffic flow "
            "to reduce sudden stops.".format(harsh_braking_events)
        )
    elif harsh_braking_events >= 2:
        recommendations.append(
            "📌 BRAKING PATTERN: {} harsh braking events detected. "
            "Practice smoother deceleration by braking earlier and more gradually.".format(
                harsh_braking_events
            )
        )

    # Acceleration-related recommendations
    if rapid_acceleration_events >= 4:
        recommendations.append(
            "🚀 RAPID ACCELERATION: {} rapid acceleration events recorded. "
            "Accelerate smoothly to improve fuel efficiency and vehicle control.".format(
                rapid_acceleration_events
            )
        )
    elif rapid_acceleration_events >= 2:
        recommendations.append(
            "📌 ACCELERATION: {} rapid accelerations detected. "
            "Gradual acceleration is safer and more economical.".format(
                rapid_acceleration_events
            )
        )

    # Cornering-related recommendations
    if cornering_speed > 60:
        recommendations.append(
            "↪️ CORNERING SPEED: Reduce speed before turns. "
            "High-speed cornering compromises vehicle stability and traction."
        )

    # Behavior class specific recommendations
    if behavior_class == 'Safe':
        recommendations.append(
            "✅ EXCELLENT: You're demonstrating safe driving habits! "
            "Continue maintaining this level of awareness and caution."
        )
    elif behavior_class == 'Moderate':
        recommendations.append(
            "📊 MODERATE RISK: Focus on the areas mentioned above "
            "to improve your safety score. Small adjustments can make a big difference."
        )
    elif behavior_class == 'Risky':
        recommendations.append(
            "⚠️ HIGH RISK: Your driving patterns show significant risk factors. "
            "Please address all recommendations above urgently. "
            "Consider defensive driving courses."
        )

    # Join all recommendations
    if recommendations:
        return "\n\n".join(recommendations)
    else:
        return "✅ Good driving pattern detected. Continue driving safely!"


def analyze_driver_behavior(driving_data: dict) -> dict:
    """
    Main analysis function that processes driving data and returns
    complete analysis results.

    Args:
        driving_data: Dictionary containing driving metrics
            {
                'average_speed': float,
                'max_speed': float,
                'harsh_braking_events': int,
                'rapid_acceleration_events': int,
                'cornering_speed': float,
            }

    Returns:
        Dictionary containing:
            {
                'risk_score': float,
                'behavior_class': str,
                'recommendations': str,
                'safety_percentage': float,
            }
    """
    # Extract data
    avg_speed = driving_data.get('average_speed', 0)
    max_speed = driving_data.get('max_speed', 0)
    braking_events = driving_data.get('harsh_braking_events', 0)
    acceleration_events = driving_data.get('rapid_acceleration_events', 0)
    corner_speed = driving_data.get('cornering_speed', 0)

    # Calculate risk score
    risk_score = calculate_risk_score(
        avg_speed, max_speed, braking_events, acceleration_events, corner_speed
    )

    # Classify behavior
    behavior_class = classify_behavior(risk_score)

    # Generate recommendations
    recommendations = generate_recommendations(
        avg_speed,
        max_speed,
        braking_events,
        acceleration_events,
        corner_speed,
        risk_score,
        behavior_class,
    )

    # Calculate safety percentage
    safety_percentage = round(100 - risk_score, 2)

    return {
        'risk_score': risk_score,
        'behavior_class': behavior_class,
        'recommendations': recommendations,
        'safety_percentage': safety_percentage,
    }


# Example usage and testing
if __name__ == "__main__":
    # Test case 1: Safe driver
    test_safe = {
        'average_speed': 45,
        'max_speed': 65,
        'harsh_braking_events': 0,
        'rapid_acceleration_events': 1,
        'cornering_speed': 30,
    }
    result_safe = analyze_driver_behavior(test_safe)
    print("=== SAFE DRIVER ===")
    print(f"Risk Score: {result_safe['risk_score']}")
    print(f"Behavior: {result_safe['behavior_class']}")
    print(f"Safety: {result_safe['safety_percentage']}%")
    print(f"Recommendations:\n{result_safe['recommendations']}")
    print()

    # Test case 2: Risky driver
    test_risky = {
        'average_speed': 95,
        'max_speed': 145,
        'harsh_braking_events': 6,
        'rapid_acceleration_events': 5,
        'cornering_speed': 70,
    }
    result_risky = analyze_driver_behavior(test_risky)
    print("=== RISKY DRIVER ===")
    print(f"Risk Score: {result_risky['risk_score']}")
    print(f"Behavior: {result_risky['behavior_class']}")
    print(f"Safety: {result_risky['safety_percentage']}%")
    print(f"Recommendations:\n{result_risky['recommendations']}")
