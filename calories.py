def calculate_calories(activity_type, duration, intensity):
    """
    Rough MET-based calorie estimation.
    MET values:
        Walking = 3.5
        Cycling = 7
        Running = 9.8
        Gym = 6
        Yoga = 3

    Formula:
        Calories = MET × 3.5 × weight(kg) / 200 × duration(minutes)

    Assume average weight of 70 kg for now.
    """

    MET_VALUES = {"Walking": 3.5, "Cycling": 7, "Running": 9.8, "Gym": 6, "Yoga": 3}

    # Adjust MET slightly based on intensity
    INTENSITY_MULTIPLIER = {"Low": 0.9, "Medium": 1.0, "High": 1.2}

    base_met = MET_VALUES.get(activity_type, 4)
    multiplier = INTENSITY_MULTIPLIER.get(intensity, 1.0)

    effective_met = base_met * multiplier

    weight = 70  # assumed
    calories = effective_met * 3.5 * weight / 200 * duration

    return round(calories, 1)
