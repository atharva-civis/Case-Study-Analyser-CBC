# Case Study Assessment Areas and Criteria
# Based on CBC-India AGK Case Study Review Rubric

# Define the four main assessment areas with weights
ASSESSMENT_AREAS = {
    "area1": {
        "name": "Structure, Chronology & Logical Flow",
        "description": "Evaluates whether the case study is well-organised, follows a logical sequence, and maintains reader engagement.",
        "total_points": 12,
        "weight": 0.25
    },
    "area2": {
        "name": "Language, Citations & Factual Accuracy",
        "description": "Ensures the case study is readable, accurate, and meets editorial and academic standards.",
        "total_points": 9,
        "weight": 0.20
    },
    "area3": {
        "name": "Alignment with Teaching Note, Sector & Competencies",
        "description": "Checks whether the case and its teaching note complement each other and align with sectoral or competency goals.",
        "total_points": 8,
        "weight": 0.25
    },
    "area4": {
        "name": "Overall Effectiveness & Impact",
        "description": "Measures how well the case study achieves its intended educational and practical outcomes.",
        "total_points": 8,
        "weight": 0.30
    }
}

# Define the specific criteria for each assessment area
ASSESSMENT_CRITERIA = {
    "area1": {
        "key_theme_clarity": {
            "name": "Key Theme Clarity",
            "description": "Is the central problem or theme clearly stated and consistently reinforced throughout the case?",
            "prompt": "Identify if the central problem or theme is clearly stated and consistently reinforced throughout the case. Summarise the main theme in ≤ 40 words.",
            "max_score": 3,
            "scoring_logic": "3 = clear & consistent; 2 = implied; 1 = vague; 0 = missing"
        },
        "chronological_flow": {
            "name": "Chronological Flow",
            "description": "Do events follow a logical, time-ordered sequence that aids reader comprehension?",
            "prompt": "Check whether events follow a logical, time-ordered sequence aiding reader comprehension.",
            "max_score": 2,
            "scoring_logic": "2 = coherent timeline; 1 = partially ordered; 0 = confusing"
        },
        "logical_coherence": {
            "name": "Logical Coherence",
            "description": "Do arguments/events build naturally on one another?",
            "prompt": "Examine if arguments/events build naturally on one another.",
            "max_score": 2,
            "scoring_logic": "2 = strong causal flow; 1 = some gaps; 0 = disjointed"
        },
        "sectional_connectivity": {
            "name": "Sectional Connectivity",
            "description": "Does each section connect smoothly with the previous one, forming a unified narrative?",
            "prompt": "Evaluate whether each section connects smoothly with the previous one, forming a unified narrative.",
            "max_score": 2,
            "scoring_logic": "2 = connected; 1 = partially; 0 = fragmented"
        },
        "template_adherence": {
            "name": "Template Adherence",
            "description": "Are all AGK template headings present and complete?",
            "prompt": "Verify that all AGK template headings are present and complete.",
            "max_score": 2,
            "scoring_logic": "2 = complete; 1 = partial; 0 = missing"
        },
        "captivating_hook": {
            "name": "Captivating Hook",
            "description": "Does the introduction capture attention and set the case context effectively?",
            "prompt": "Assess whether the introduction captures attention and sets the case context effectively.",
            "max_score": 1,
            "scoring_logic": "1 = engaging; 0 = flat"
        }
    },
    "area2": {
        "language_quality": {
            "name": "Language Quality",
            "description": "Does the text use clear, simple, British English; avoids passive voice and jargon?",
            "prompt": "Evaluate if the text uses clear, simple, British English; avoids passive voice and jargon.",
            "max_score": 3,
            "scoring_logic": "3 = clear & active; 2 = minor issues; 1 = wordy/passive; 0 = poor"
        },
        "factual_correctness": {
            "name": "Factual Correctness",
            "description": "Are facts/data/events accurate and supported by citations or references?",
            "prompt": "Verify whether facts/data/events are accurate and supported by citations or references.",
            "max_score": 3,
            "scoring_logic": "3 = verified; 2 = minor gaps; 1 = questionable; 0 = unverified"
        },
        "citation_quality": {
            "name": "Citation Quality",
            "description": "Are citations valid, functional, and properly formatted?",
            "prompt": "Check if citations are valid, functional, and properly formatted.",
            "max_score": 2,
            "scoring_logic": "2 = all verified; 1 = partially; 0 = broken/missing"
        },
        "additional_readings": {
            "name": "Additional Readings",
            "description": "Are recommended supplementary materials or related cases present?",
            "prompt": "Look for the presence of recommended supplementary materials or related cases.",
            "max_score": 1,
            "scoring_logic": "1 = present; 0 = absent"
        }
    },
    "area3": {
        "learning_objectives_alignment": {
            "name": "Learning Objectives Alignment",
            "description": "Does the case content support the teaching note's stated learning objectives?",
            "prompt": "Cross-check if the case content supports the teaching note's stated learning objectives.",
            "max_score": 3,
            "scoring_logic": "3 = fully aligned; 2 = partial; 1 = weak; 0 = not aligned"
        },
        "theories_frameworks": {
            "name": "Theories & Frameworks",
            "description": "Does the TN include relevant theoretical or analytical frameworks linked to the case?",
            "prompt": "Identify whether the TN includes relevant theoretical or analytical frameworks linked to the case.",
            "max_score": 2,
            "scoring_logic": "2 = present & used; 1 = named but unused; 0 = missing"
        },
        "competency_alignment": {
            "name": "Competency Alignment",
            "description": "Are Karmayogi competencies mapped appropriately and evident in the narrative?",
            "prompt": "Evaluate mapping of Karmayogi competencies—are they appropriate and evident in the narrative?",
            "max_score": 2,
            "scoring_logic": "2 = strong; 1 = weak; 0 = absent"
        },
        "sector_theme_classification": {
            "name": "Sector / Theme Classification (SDG Linkage)",
            "description": "Is the case tagged to the correct sector or SDG theme?",
            "prompt": "Confirm that the case is tagged to the correct sector or SDG theme.",
            "max_score": 1,
            "scoring_logic": "1 = correct; 0 = misclassified"
        }
    },
    "area4": {
        "delivery_implementation_clarity": {
            "name": "Delivery & Implementation Clarity",
            "description": "Are problems and solutions clearly articulated, and is implementation described logically?",
            "prompt": "Assess if problems and solutions are clearly articulated, and whether implementation is described logically.",
            "max_score": 3,
            "scoring_logic": "3 = clear; 2 = partial; 1 = ambiguous; 0 = missing"
        },
        "best_practices_lessons": {
            "name": "Best Practices & Lessons",
            "description": "Are explicit best practices, lessons learned, or innovative methods emerging from the narrative?",
            "prompt": "Detect explicit best practices, lessons learned, or innovative methods emerging from the narrative.",
            "max_score": 2,
            "scoring_logic": "2 = evident; 1 = weak; 0 = missing"
        },
        "impact_visibility": {
            "name": "Impact Visibility",
            "description": "Are results, transformations, or measurable outcomes described and substantiated?",
            "prompt": "Check if the results, transformations, or measurable outcomes are described and substantiated.",
            "max_score": 3,
            "scoring_logic": "3 = visible & supported; 2 = partial; 1 = minimal; 0 = absent"
        }
    }
}

def calculate_weighted_score(assessment_results):
    """
    Calculate the weighted composite score based on assessment results.
    
    Formula: Final Composite Score = Σ (weighted area scores) × 100 (%)
    Where weighted area score = weight × (score / total_points)
    
    Args:
        assessment_results: Dictionary containing scores for each criterion
        
    Returns:
        Dictionary with area scores, weighted scores, and final composite score
    """
    area_scores = {}
    weighted_scores = {}
    
    for area_id, area_info in ASSESSMENT_AREAS.items():
        total_points = area_info["total_points"]
        weight = area_info["weight"]
        
        # Sum up scores for all criteria in this area
        area_score = 0
        if area_id in assessment_results:
            for criterion_id, result in assessment_results[area_id].items():
                score = result.get("score", 0)
                area_score += score
        
        area_scores[area_id] = {
            "score": area_score,
            "max_score": total_points,
            "percentage": (area_score / total_points * 100) if total_points > 0 else 0
        }
        
        # Calculate weighted contribution
        weighted_contribution = weight * (area_score / total_points) if total_points > 0 else 0
        weighted_scores[area_id] = {
            "weight": weight,
            "weighted_contribution": weighted_contribution
        }
    
    # Calculate final composite score
    final_score = sum(ws["weighted_contribution"] for ws in weighted_scores.values()) * 100
    
    return {
        "area_scores": area_scores,
        "weighted_scores": weighted_scores,
        "final_composite_score": final_score
    }

def get_score_color(score, max_score):
    """
    Get color based on score percentage.
    
    Args:
        score: The actual score
        max_score: The maximum possible score
        
    Returns:
        Color string for visualization
    """
    if max_score == 0:
        return "#808080"  # Gray for undefined
    
    percentage = score / max_score
    
    if percentage >= 0.75:
        return "#28a745"  # Green - Excellent
    elif percentage >= 0.5:
        return "#ffc107"  # Yellow - Satisfactory
    elif percentage >= 0.25:
        return "#fd7e14"  # Orange - Needs Improvement
    else:
        return "#dc3545"  # Red - Poor

def get_grade_label(final_score):
    """
    Get grade label based on final composite score.
    
    Args:
        final_score: The final composite score (0-100)
        
    Returns:
        Grade label string
    """
    if final_score >= 85:
        return "Excellent"
    elif final_score >= 70:
        return "Good"
    elif final_score >= 55:
        return "Satisfactory"
    elif final_score >= 40:
        return "Needs Improvement"
    else:
        return "Poor"
