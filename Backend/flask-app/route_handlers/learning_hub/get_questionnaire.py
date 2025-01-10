import numpy as np
import os
import uuid
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Physical Activity Guidelines
GUIDELINES = {
    "outdoor_play": {"min_days": 5, "min_minutes": 60},
    "screen_time": {"max_hours": 2},
    "physical_education": {"min_classes": 2},
    "active_days": {"min_days": 5}
}

def assess_activity(outdoor_play_days, outdoor_play_minutes, screen_time, physical_education, active_days, walk_or_cycle):
    """
    Assess the child's physical activity against defined guidelines.

    Returns:
        - A dictionary containing scores, status, and recommendations.
    """
    result = {"status": [], "recommendations": [], "scores": {}}

    # Outdoor Play Assessment
    result['scores']['outdoor_play_days'] = min(outdoor_play_days / GUIDELINES['outdoor_play']['min_days'] * 100, 100)
    result['scores']['outdoor_play_minutes'] = min(outdoor_play_minutes / GUIDELINES['outdoor_play']['min_minutes'] * 100, 100)

    if outdoor_play_days >= GUIDELINES['outdoor_play']['min_days'] and outdoor_play_minutes >= GUIDELINES['outdoor_play']['min_minutes']:
        result['status'].append({'meets_criteria': True, 'aspect': 'Outdoor Play', 'text': "Meets recommended levels of at least 5 days per week and 60 minutes per day."})
    elif outdoor_play_days >= GUIDELINES['outdoor_play']['min_days']:
        result['status'].append({'meets_criteria': True, 'aspect': 'Outdoor Play', 'text': "Days are sufficient, but less than 60 minutes per day."})
        result['recommendations'].append("Encourage at least 60 minutes of outdoor play daily.")
    else:
        result['status'].append({'meets_criteria': False, 'aspect': 'Outdoor Play', 'text': "Below recommended levels for both days and minutes."})
        result['recommendations'].append("Increase outdoor play to 5 days a week with at least 60 minutes each day.")

    # Screen Time Assessment
    if screen_time <= GUIDELINES['screen_time']['max_hours']:
        result['scores']['screen_time'] = 100
        result['status'].append({'meets_criteria': True, 'aspect': 'Screen Time', 'text': "Within recommended limits (2 hours or less per day)."})
    else:
        result['scores']['screen_time'] = max(0, 100 - ((screen_time - GUIDELINES['screen_time']['max_hours']) * 50))
        result['status'].append({'meets_criteria': False, 'aspect': 'Screen Time', 'text': "Above recommended levels."})
        result['recommendations'].append("Reduce screen time to 2 hours or less daily.")

    # Physical Education Assessment
    result['scores']['physical_education'] = min(physical_education / GUIDELINES['physical_education']['min_classes'] * 100, 100)
    if physical_education >= GUIDELINES['physical_education']['min_classes']:
        result['status'].append({'meets_criteria': True, 'aspect': 'Physical Education', 'text': "Meets recommended levels."})
    else:
        result['status'].append({'meets_criteria': False, 'aspect': 'Physical Education', 'text': "Below recommended levels."})
        result['recommendations'].append("Participate in at least 2 physical education classes per week.")

    # Active Days Assessment
    result['scores']['active_days'] = min(active_days / GUIDELINES['active_days']['min_days'] * 100, 100)
    if active_days >= GUIDELINES['active_days']['min_days']:
        result['status'].append({'meets_criteria': True, 'aspect': 'Active Days', 'text': "Meets recommended levels."})
    else:
        result['status'].append({'meets_criteria': False, 'aspect': 'Active Days', 'text': "Below recommended levels."})
        result['recommendations'].append("Engage in heart-rate-increasing activities 5 days per week.")

    # Walking or Cycling Assessment
    if "most of the time" in walk_or_cycle.lower():
        result['scores']['walk_or_cycle'] = 100
        result['status'].append({'meets_criteria': True, 'aspect': 'Active Transportation', 'text': "Walking or cycling regularly (5+ days per week)."})
    elif "sometimes" in walk_or_cycle.lower():
        result['scores']['walk_or_cycle'] = 50
        result['status'].append({'meets_criteria': True, 'aspect': 'Active Transportation', 'text': "Walking or cycling occasionally."})
        result['recommendations'].append("Increase walking or cycling to 5+ days per week.")
    else:
        result['scores']['walk_or_cycle'] = 0
        result['status'].append({'meets_criteria': False, 'aspect': 'Active Transportation', 'text': "Not walking or cycling regularly."})
        result['recommendations'].append("Encourage walking or cycling daily.")

    return result


def create_spider_chart(scores):
    """
    Generate a spider chart to visualize the assessment results.
    
    Returns:
        - The file path of the saved chart.
    """
    categories = ['Outdoor Play (Days)', 'Outdoor Play (Minutes)', 'Screen Time', 'Physical Education', 'Active Days', 'Walking/Cycling']
    values = [scores[category.lower().replace(' ', '_')] for category in categories]
    values += values[:1]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Plot the recommended and actual values
    ax.fill(angles, [100] * len(categories) + [100], color='lightgray', alpha=0.4, label='Recommended')
    ax.fill(angles, values, color='#00c92f', alpha=0.6, label='Performance')

    # Styling
    ax.set_ylim(0, 100)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, color='darkgreen')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

    # Save the chart
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    chart_filename = f"static/images/parent/spider_chart_{timestamp}_{unique_id}.png"
    os.makedirs(os.path.dirname(chart_filename), exist_ok=True)
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    plt.close()

    return chart_filename
