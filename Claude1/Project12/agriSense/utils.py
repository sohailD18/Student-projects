from typing import List, Dict, Any
from django.db.models import Q, Avg
from .models import Crop, Season, SoilData, YieldRecord


def recommend_crops(soil_type: str = None, season: str = None) -> List[Dict[str, Any]]:
    """
    Recommend crops based on soil type and/or season.

    Args:
        soil_type: The soil type (e.g., 'clay', 'loamy', 'sandy')
        season: The season name (e.g., 'Spring', 'Summer', 'Kharif')

    Returns:
        List of dictionaries containing crop information with suitability scores
    """
    crops = Crop.objects.all()
    results = []

    for crop in crops:
        score = 0
        max_score = 0
        reasons = []

        # Check soil type suitability
        if soil_type:
            max_score += 1
            if crop.suitable_soil_types and soil_type in crop.suitable_soil_types:
                score += 1
                reasons.append(f"Suitable for {soil_type} soil")
            else:
                reasons.append(f"Not ideal for {soil_type} soil")

        # Check season suitability
        if season:
            max_score += 1
            season_obj = crop.suitable_seasons.filter(name__iexact=season).first()
            if season_obj:
                score += 1
                reasons.append(f"Suitable for {season} season")
            else:
                reasons.append(f"Not ideal for {season} season")

        # Calculate suitability percentage
        suitability_percent = (score / max_score * 100) if max_score > 0 else 100

        crop_info = {
            'id': crop.id,
            'name': crop.name,
            'type': crop.get_type_display(),
            'duration': crop.duration,
            'suitability_score': score,
            'max_score': max_score,
            'suitability_percent': round(suitability_percent, 2),
            'reasons': reasons
        }

        # Include average yield if available
        avg_yield = YieldRecord.objects.filter(crop=crop).aggregate(
            avg_quantity=Avg('quantity')
        )['avg_quantity']

        if avg_yield:
            crop_info['average_yield'] = round(float(avg_yield), 2)

        results.append(crop_info)

    # Sort by suitability score (descending)
    results.sort(key=lambda x: x['suitability_percent'], reverse=True)

    return results


def recommend_crops_by_ph(ph_level: float) -> List[Dict[str, Any]]:
    """
    Recommend crops based on soil pH level.

    Args:
        ph_level: The pH level of the soil (0-14)

    Returns:
        List of crops suitable for the given pH with recommendations
    """
    crops = Crop.objects.all()
    results = []

    for crop in crops:
        # Get recent soil data for this crop's suitable soil types
        suitable_soils = crop.suitable_soil_types or []
        if not suitable_soils:
            continue

        recent_soil_data = SoilData.objects.filter(
            type__in=suitable_soils
        ).order_by('-recorded_date').first()

        if recent_soil_data:
            ph_diff = abs(float(recent_soil_data.ph) - ph_level)
            # Smaller difference = better match
            if ph_diff <= 1.0:
                suitability = "Excellent"
            elif ph_diff <= 2.0:
                suitability = "Good"
            elif ph_diff <= 3.0:
                suitability = "Moderate"
            else:
                suitability = "Poor"

            results.append({
                'crop': crop.name,
                'soil_type': recent_soil_data.type,
                'soil_ph': float(recent_soil_data.ph),
                'your_ph': ph_level,
                'ph_difference': round(ph_diff, 2),
                'suitability': suitability
            })

    results.sort(key=lambda x: x['ph_difference'])
    return results


def get_seasonal_calendar(season: str = None) -> List[Dict[str, Any]]:
    """
    Get a seasonal calendar of crops.

    Args:
        season: Optional season to filter by

    Returns:
        List of crops organized by season
    """
    if season:
        seasons = Season.objects.filter(name__iexact=season)
    else:
        seasons = Season.objects.all()

    calendar = []
    for s in seasons:
        crops = s.crops.all()
        calendar.append({
            'season': s.name,
            'months': s.months,
            'crops': [{'name': c.name, 'type': c.type, 'duration': c.duration} for c in crops]
        })

    return calendar


def analyze_yield_trends(crop_name: str) -> Dict[str, Any]:
    """
    Analyze yield trends for a specific crop.

    Args:
        crop_name: Name of the crop to analyze

    Returns:
        Dictionary containing yield analysis
    """
    try:
        crop = Crop.objects.get(name__iexact=crop_name)
    except Crop.DoesNotExist:
        return {'error': f'Crop "{crop_name}" not found'}

    yield_records = YieldRecord.objects.filter(crop=crop).order_by('year')

    if not yield_records.exists():
        return {'error': f'No yield records found for {crop_name}'}

    quantities = [float(y.quantity) for y in yield_records]

    # Calculate trends
    avg_yield = sum(quantities) / len(quantities)
    max_yield = max(quantities)
    min_yield = min(quantities)

    # Simple trend calculation
    if len(quantities) >= 2:
        trend = quantities[-1] - quantities[0]
        trend_percent = (trend / quantities[0]) * 100 if quantities[0] > 0 else 0
    else:
        trend = 0
        trend_percent = 0

    return {
        'crop': crop.name,
        'years_recorded': len(yield_records),
        'average_yield': round(avg_yield, 2),
        'max_yield': round(max_yield, 2),
        'min_yield': round(min_yield, 2),
        'trend': round(trend, 2),
        'trend_percent': round(trend_percent, 2),
        'records': [
            {
                'year': y.year,
                'quantity': float(y.quantity),
                'recorded_date': y.recorded_date.strftime('%Y-%m-%d')
            }
            for y in yield_records
        ]
    }


def get_top_performing_crops(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get top performing crops based on average yield.

    Args:
        limit: Number of top crops to return

    Returns:
        List of top performing crops
    """
    crops = Crop.objects.annotate(
        avg_yield=Avg('yield_records__quantity')
    ).filter(avg_yield__isnull=False).order_by('-avg_yield')[:limit]

    return [
        {
            'name': crop.name,
            'type': crop.get_type_display(),
            'average_yield': round(float(crop.avg_yield), 2),
            'records_count': crop.yield_records.count()
        }
        for crop in crops
    ]


def predict_yield(crop_name: str, area_acres: float) -> Dict[str, Any]:
    """
    Predict yield for a crop based on area.

    Args:
        crop_name: Name of the crop
        area_acres: Area in acres

    Returns:
        Dictionary containing prediction results
    """
    try:
        crop = Crop.objects.get(name__iexact=crop_name)
    except Crop.DoesNotExist:
        return {
            'error': f'Crop "{crop_name}" not found',
            'crop': crop_name,
            'area_acres': area_acres
        }

    # Get historical yield data
    yield_records = YieldRecord.objects.filter(crop=crop).order_by('-year')

    if not yield_records.exists():
        return {
            'error': f'No yield records found for {crop_name}',
            'crop': crop_name,
            'area_acres': area_acres,
            'note': 'Please add historical yield data for accurate predictions'
        }

    # Calculate average yield (in tons per hectare)
    avg_yield_per_hectare = yield_records.aggregate(
        avg_yield=Avg('quantity')
    )['avg_yield']

    # Convert: 1 hectare = 2.47105 acres
    # yield per acre = yield per hectare / 2.47105
    yield_per_acre = float(avg_yield_per_hectare) / 2.47105

    # Calculate predicted yield
    predicted_yield = yield_per_acre * area_acres

    # Get trend for confidence estimation
    recent_yields = list(yield_records.order_by('-year')[:3].values_list('quantity', flat=True))
    if len(recent_yields) >= 2:
        trend = recent_yields[0] - recent_yields[-1]
        if trend > 0:
            confidence = "High (yield trend increasing)"
        elif trend < 0:
            confidence = "Moderate (yield trend decreasing)"
        else:
            confidence = "Moderate (stable yield)"
    else:
        confidence = "Low (limited data)"

    return {
        'crop': crop.name,
        'crop_type': crop.get_type_display(),
        'area_acres': area_acres,
        'area_hectares': round(area_acres / 2.47105, 2),
        'average_yield_tons_per_hectare': round(float(avg_yield_per_hectare), 2),
        'average_yield_tons_per_acre': round(yield_per_acre, 2),
        'predicted_yield_tons': round(predicted_yield, 2),
        'predicted_yield_kg': round(predicted_yield * 1000, 2),
        'confidence': confidence,
        'years_of_data': yield_records.count(),
        'yield_range_tons_per_hectare': {
            'min': float(yield_records.aggregate(min_yield=Avg('quantity'))['min_yield']) * 0.9,
            'max': float(yield_records.aggregate(max_yield=Avg('quantity'))['max_yield']) * 1.1,
        }
    }


def assess_pest_risk(season: str) -> Dict[str, Any]:
    """
    Assess pest risk level based on season.

    Args:
        season: The season name

    Returns:
        Dictionary containing risk assessment
    """
    # Pest risk data by season
    pest_risk_data = {
        'spring': {
            'risk_level': 'Medium',
            'risk_score': 5,
            'common_pests': [
                'Aphids',
                'Cutworms',
                'Armyworms',
                'Flea beetles'
            ],
            'preventive_measures': [
                'Use row covers to protect young plants',
                'Rotate crops to break pest cycles',
                'Introduce beneficial insects (ladybugs, lacewings)',
                'Monitor for early signs of infestation'
            ],
            'weather_factor': 'Mild temperatures promote pest activity'
        },
        'summer': {
            'risk_level': 'High',
            'risk_score': 8,
            'common_pests': [
                ' locusts',
                'Grasshoppers',
                'Spider mites',
                'Thrips',
                'Whiteflies',
                'Corn earworms'
            ],
            'preventive_measures': [
                'Ensure proper irrigation to reduce plant stress',
                'Apply neem oil or insecticidal soap',
                'Use pheromone traps for monitoring',
                'Maintain proper plant spacing for airflow'
            ],
            'weather_factor': 'Hot and humid conditions accelerate pest reproduction'
        },
        'autumn': {
            'risk_level': 'Medium',
            'risk_score': 4,
            'common_pests': [
                'Cabbage loopers',
                'Slugs',
                'Snails',
                'Fall armyworms'
            ],
            'preventive_measures': [
                'Remove crop debris and weeds',
                'Use copper tape for slug control',
                'Apply biological pesticides (Bt)',
                'Harvest promptly to minimize exposure'
            ],
            'weather_factor': 'Cooler temperatures reduce but dont eliminate pest activity'
        },
        'winter': {
            'risk_level': 'Low',
            'risk_score': 2,
            'common_pests': [
                'Rodents',
                'Birds',
                'Overwintering insects'
            ],
            'preventive_measures': [
                'Clean field of crop residues',
                'Use physical barriers for rodent control',
                'Apply dormant oil sprays to fruit trees',
                'Maintain sanitation to prevent overwintering'
            ],
            'weather_factor': 'Cold temperatures naturally suppress most pests'
        },
        'monsoon': {
            'risk_level': 'High',
            'risk_score': 9,
            'common_pests': [
                'Fungal infections',
                'Root rot',
                'Leaf spot diseases',
                'Stem borers',
                'Gall midges'
            ],
            'preventive_measures': [
                'Ensure proper drainage to prevent waterlogging',
                'Apply fungicides preventatively',
                'Use resistant crop varieties',
                'Avoid overhead irrigation'
            ],
            'weather_factor': 'Excess moisture creates ideal conditions for pests and diseases'
        },
        'kharif': {
            'risk_level': 'High',
            'risk_score': 8,
            'common_pests': [
                'Stem borers',
                'Brown plant hopper',
                'Leaf folder',
                'Gall midge',
                'Shoot fly'
            ],
            'preventive_measures': [
                'Use pest-resistant varieties',
                'Install light traps to monitor adult populations',
                'Release Trichogramma eggs for biological control',
                'Apply need-based insecticide applications'
            ],
            'weather_factor': 'Heavy rainfall promotes pest and disease pressure'
        },
        'rabi': {
            'risk_level': 'Low to Medium',
            'risk_score': 3,
            'common_pests': [
                'Aphids',
                'Termites',
                'Armyworms',
                'Pod borers'
            ],
            'preventive_measures': [
                'Use certified disease-free seeds',
                'Practice deep summer plowing',
                'Maintain optimal plant density',
                'Apply seed treatments where appropriate'
            ],
            'weather_factor': 'Dryer conditions limit pest reproduction'
        }
    }

    season_key = season.lower()
    result = pest_risk_data.get(season_key, {
        'risk_level': 'Unknown',
        'risk_score': 0,
        'common_pests': ['Data not available'],
        'preventive_measures': ['Consult local agricultural extension'],
        'weather_factor': 'No data available for this season'
    })

    return {
        'season': season,
        'risk_level': result['risk_level'],
        'risk_score': result['risk_score'],
        'common_pests': result['common_pests'],
        'preventive_measures': result['preventive_measures'],
        'weather_factor': result['weather_factor'],
        'recommendation': _get_risk_recommendation(result['risk_score'])
    }


def _get_risk_recommendation(score: int) -> str:
    """Get recommendation based on risk score."""
    if score >= 7:
        return "Implement integrated pest management (IPM) immediately. Monitor fields daily."
    elif score >= 4:
        return "Regular monitoring recommended. Be prepared to implement control measures."
    else:
        return "Continue standard monitoring practices. Risk is minimal."


def suggest_fertilizer(crop_name: str) -> Dict[str, Any]:
    """
    Suggest fertilizer schedule based on crop.

    Args:
        crop_name: Name of the crop

    Returns:
        Dictionary containing fertilizer schedule
    """
    # Fertilizer database by crop
    fertilizer_data = {
        'wheat': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 20:60:40 (basal) + 33:0:0 (top dressing)',
            'schedule': [
                {
                    'stage': 'At Sowing',
                    'days': 0,
                    'fertilizer': 'DAP (50 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal application, mix with soil'
                },
                {
                    'stage': 'First Irrigation (CRI)',
                    'days': 21,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Top dressing, apply before first irrigation'
                },
                {
                    'stage': 'Second Irrigation',
                    'days': 45,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Top dressing, apply before second irrigation'
                },
                {
                    'stage': 'Late Tillering',
                    'days': 60,
                    'fertilizer': 'Urea (11 kg/acre)',
                    'application': 'Final top dressing if needed'
                }
            ],
            'micronutrients': ['Zinc sulfate (10 kg/acre)', 'Iron sulfate (5 kg/acre)'],
            'organic_alternatives': [
                'Farmyard manure: 5-10 tons/acre at sowing',
                'Vermicompost: 2-3 tons/acre',
                'Neem cake: 100 kg/acre'
            ]
        },
        'rice': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 60:40:40',
            'schedule': [
                {
                    'stage': 'At Last Plowing',
                    'days': 0,
                    'fertilizer': 'DAP (40 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal, incorporate into soil'
                },
                {
                    'stage': 'Active Tillering',
                    'days': 20,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Top dressing, 3 days after first irrigation'
                },
                {
                    'stage': 'Panicle Initiation',
                    'days': 45,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Top dressing'
                },
                {
                    'stage': 'Heading Stage',
                    'days': 70,
                    'fertilizer': 'Urea (11 kg/acre)',
                    'application': 'Final top dressing'
                }
            ],
            'micronutrients': ['Zinc sulfate (25 kg/acre)', 'Iron sulfate (10 kg/acre)'],
            'organic_alternatives': [
                'Green manuring with dhaincha',
                'Farmyard manure: 8-10 tons/acre',
                'Neem cake coated urea'
            ]
        },
        'maize': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 80:40:40',
            'schedule': [
                {
                    'stage': 'At Sowing',
                    'days': 0,
                    'fertilizer': 'DAP (50 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal application'
                },
                {
                    'stage': 'Knee High Stage (30 days)',
                    'days': 30,
                    'fertilizer': 'Urea (46 kg/acre)',
                    'application': 'First top dressing, band placement'
                },
                {
                    'stage': 'Tasseling Stage',
                    'days': 60,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Second top dressing'
                }
            ],
            'micronutrients': ['Zinc sulfate (15 kg/acre)', 'Boron (2 kg/acre)'],
            'organic_alternatives': [
                'Farmyard manure: 10 tons/acre',
                'Vermicompost: 3 tons/acre',
                'Bio-fertilizers: Azotobacter + PSB'
            ]
        },
        'tomato': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 100:60:60',
            'schedule': [
                {
                    'stage': 'At Transplanting',
                    'days': 0,
                    'fertilizer': 'DAP (40 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal application in pits'
                },
                {
                    'stage': '3 Weeks After Transplanting',
                    'days': 21,
                    'fertilizer': 'Calcium Ammonium Nitrate (40 kg/acre)',
                    'application': 'Ring application around plants'
                },
                {
                    'stage': 'Flowering Stage',
                    'days': 45,
                    'fertilizer': '19:19:19 NPK (20 kg/acre)',
                    'application': 'Foliar spray or soil application'
                },
                {
                    'stage': 'Fruit Development',
                    'days': 60,
                    'fertilizer': 'Potassium nitrate (10 kg/acre)',
                    'application': 'For better fruit quality'
                }
            ],
            'micronutrients': ['Calcium nitrate', 'Magnesium sulfate', 'Borax'],
            'organic_alternatives': [
                'Well-decomposed FYM: 8 tons/acre',
                'Neem cake: 200 kg/acre',
                'Bio-fertilizers at transplanting'
            ]
        },
        'potato': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 180:80:100',
            'schedule': [
                {
                    'stage': 'At Planting',
                    'days': 0,
                    'fertilizer': 'DAP (80 kg/acre) + MOP (60 kg/acre)',
                    'application': 'Basal, mix with soil before planting'
                },
                {
                    'stage': '30 Days After Planting',
                    'days': 30,
                    'fertilizer': 'Urea (33 kg/acre) + MOP (40 kg/acre)',
                    'application': 'Top dressing and earthing up'
                },
                {
                    'stage': '60 Days After Planting',
                    'days': 60,
                    'fertilizer': 'MOP (40 kg/acre)',
                    'application': 'Final top dressing'
                }
            ],
            'micronutrients': ['Magnesium sulfate (15 kg/acre)', 'Boron (2 kg/acre)'],
            'organic_alternatives': [
                'Well-rotted FYM: 10-15 tons/acre',
                'Vermicompost: 5 tons/acre',
                'Neem cake: 150 kg/acre'
            ]
        },
        'cotton': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 80:40:40',
            'schedule': [
                {
                    'stage': 'At Sowing',
                    'days': 0,
                    'fertilizer': 'DAP (50 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal application'
                },
                {
                    'stage': 'Square Formation',
                    'days': 60,
                    'fertilizer': 'Urea (46 kg/acre)',
                    'application': 'First top dressing'
                },
                {
                    'stage': 'Flowering & Boll Formation',
                    'days': 90,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Second top dressing'
                }
            ],
            'micronutrients': ['Zinc sulfate (20 kg/acre)', 'Iron sulfate (10 kg/acre)'],
            'organic_alternatives': [
                'FYM: 8 tons/acre',
                'Neem cake: 150 kg/acre',
                'Bio-fertilizers: Azospirillum'
            ]
        },
        'sugarcane': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 200:80:120',
            'schedule': [
                {
                    'stage': 'At Planting',
                    'days': 0,
                    'fertilizer': 'DAP (80 kg/acre) + MOP (80 kg/acre)',
                    'application': 'Basal application in furrows'
                },
                {
                    'stage': '3 Months After Planting',
                    'days': 90,
                    'fertilizer': 'Urea (46 kg/acre) + MOP (40 kg/acre)',
                    'application': 'First top dressing'
                },
                {
                    'stage': '6 Months After Planting',
                    'days': 180,
                    'fertilizer': 'Urea (69 kg/acre)',
                    'application': 'Second top dressing'
                },
                {
                    'stage': '9 Months After Planting',
                    'days': 270,
                    'fertilizer': 'Urea (46 kg/acre)',
                    'application': 'Final top dressing'
                }
            ],
            'micronutrients': ['Zinc sulfate (25 kg/acre)', 'Iron sulfate (15 kg/acre)', 'Manganese (10 kg/acre)'],
            'organic_alternatives': [
                'FYM: 15 tons/acre',
                'Press mud compost: 5 tons/acre',
                'Bio-fertilizers: Azotobacter + PSB'
            ]
        },
        'soybean': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 30:60:40',
            'schedule': [
                {
                    'stage': 'At Sowing',
                    'days': 0,
                    'fertilizer': 'DAP (60 kg/acre) + MOP (20 kg/acre)',
                    'application': 'Basal application'
                },
                {
                    'stage': '30 Days After Sowing',
                    'days': 30,
                    'fertilizer': 'DAP (20 kg/acre)',
                    'application': 'Top dressing if deficiency observed'
                }
            ],
            'micronutrients': ['Molybdenum seed treatment', 'Zinc sulfate (15 kg/acre)'],
            'organic_alternatives': [
                'Rhizobium culture seed treatment',
                'FYM: 6 tons/acre',
                'Vermicompost: 2 tons/acre'
            ]
        },
        'default': {
            'nitrogen_phosphorus_potassium_ratio': 'NPK 50:40:40 (general purpose)',
            'schedule': [
                {
                    'stage': 'At Planting',
                    'days': 0,
                    'fertilizer': 'Balanced NPK fertilizer (50 kg/acre)',
                    'application': 'Basal application, mix with soil'
                },
                {
                    'stage': 'Mid-Season',
                    'days': 45,
                    'fertilizer': 'Urea (23 kg/acre)',
                    'application': 'Top dressing during active growth'
                }
            ],
            'micronutrients': ['Zinc sulfate (10 kg/acre)'],
            'organic_alternatives': [
                'Well-rotted FYM: 5-8 tons/acre',
                'Vermicompost: 2-3 tons/acre',
                'Neem cake: 100 kg/acre'
            ]
        }
    }

    crop_key = crop_name.lower()
    fertilizer_info = fertilizer_data.get(crop_key, fertilizer_data['default'])

    # Verify crop exists in database
    try:
        crop = Crop.objects.get(name__iexact=crop_name)
        crop_exists = True
    except Crop.DoesNotExist:
        crop_exists = False
        fertilizer_info = fertilizer_data['default'].copy()
        fertilizer_info['note'] = f'Crop "{crop_name}" not found in database. Showing general recommendations.'

    return {
        'crop': crop_name,
        'crop_exists': crop_exists,
        'npk_ratio': fertilizer_info['nitrogen_phosphorus_potassium_ratio'],
        'fertilizer_schedule': fertilizer_info['schedule'],
        'micronutrients': fertilizer_info['micronutrients'],
        'organic_alternatives': fertilizer_info['organic_alternatives'],
        'total_applications': len(fertilizer_info['schedule']),
        'notes': fertilizer_info.get('note', '')
    }
