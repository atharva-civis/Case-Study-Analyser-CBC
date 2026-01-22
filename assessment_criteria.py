# Case Study Assessment Areas and Criteria
# Based on CBC-India AGK Case Study Review Rubric (Updated)

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
        "total_points": 12,
        "weight": 0.20
    },
    "area3": {
        "name": "Alignment with Teaching Note, Sector & Competencies",
        "description": "Checks whether the case and its teaching note complement each other and align with sectoral or competency goals.",
        "total_points": 10,
        "weight": 0.25
    },
    "area4": {
        "name": "Overall Effectiveness & Impact",
        "description": "Measures how well the case study achieves its intended educational and practical outcomes.",
        "total_points": 13,
        "weight": 0.30
    }
}

# Define the specific criteria for each assessment area
ASSESSMENT_CRITERIA = {
    "area1": {
        "key_theme_clarity": {
            "name": "Key Theme",
            "description": "Is the central theme or problem statement clearly defined and runs consistently throughout the case?",
            "prompt": "Identify if the central theme or problem statement is clearly defined and runs consistently throughout the case. Summarise the main theme in ≤ 40 words.",
            "evaluation_approach": "Detects clarity and recurrence of central ideas.",
            "max_score": 3,
            "scoring_logic": "3 = Clear & consistent; 2 = Implied; 1 = Ambiguous; 0 = Missing"
        },
        "chronology_maintained": {
            "name": "Chronology Maintained",
            "description": "Does the sequence of events follow a logical timeline and support reader comprehension?",
            "prompt": "Check if the sequence of events follows a logical timeline and supports reader comprehension.",
            "evaluation_approach": "Sequence analysis for time markers and transitions.",
            "max_score": 2,
            "scoring_logic": "2 = Sequential; 1 = Non-linear but understandable; 0 = Confusing"
        },
        "logical_coherence": {
            "name": "Logical Coherence",
            "description": "Do arguments and events build naturally upon each other?",
            "prompt": "Verify if arguments and events build naturally upon each other. Analyze paragraph transitions and causal flow.",
            "evaluation_approach": "Analyze paragraph transitions and causal flow.",
            "max_score": 2,
            "scoring_logic": "2 = Consistent flow; 1 = Some gaps; 0 = Disjointed"
        },
        "sectional_connectivity": {
            "name": "Sectional Connectivity",
            "description": "Does each section connect smoothly with the previous one, maintaining a single narrative thread?",
            "prompt": "Ensure each section connects smoothly with the previous one, maintaining a single narrative thread.",
            "evaluation_approach": "Semantic linkage check between sections.",
            "max_score": 2,
            "scoring_logic": "2 = Connected; 1 = Partially connected; 0 = Fragmented"
        },
        "agk_template_adherence": {
            "name": "AGK Template Adherence",
            "description": "Are all required headings under the AGK template present and complete?",
            "prompt": "Evaluate whether all required headings under the AGK template are present and complete.",
            "evaluation_approach": "Structural pattern recognition.",
            "max_score": 2,
            "scoring_logic": "2 = Complete; 1 = Partial; 0 = Missing"
        },
        "captivating_hook": {
            "name": "Captivating Hook",
            "description": "Does the introduction capture attention and set context for the case?",
            "prompt": "Check if the introduction captures attention and sets context for the case effectively.",
            "evaluation_approach": "Sentiment and engagement score for the opening section.",
            "max_score": 1,
            "scoring_logic": "1 = Engaging; 0 = Flat"
        }
    },
    "area2": {
        "language_quality": {
            "name": "Language Quality",
            "description": "Does the text use simple, active, British English, past tense, avoiding passive voice or jargon?",
            "prompt": "Ensure use of simple, active, and British English, past tense, avoiding passive voice or jargon.",
            "evaluation_approach": "Grammatical pattern detection and style consistency.",
            "max_score": 3,
            "scoring_logic": "3 = Clear & active; 2 = Minor issues; 1 = Wordy/Passive; 0 = Poor"
        },
        "factual_correctness": {
            "name": "Factual Correctness",
            "description": "Are all facts, data, and events verified with cited or linked evidence?",
            "prompt": "Verify all facts, data, and events with cited or linked evidence.",
            "evaluation_approach": "Cross-reference with cited sources or databases.",
            "max_score": 3,
            "scoring_logic": "3 = Accurate; 2 = Minor gaps; 1 = Questionable; 0 = Unverified"
        },
        "tone_neutrality_bias": {
            "name": "Tone Neutrality and Bias Check",
            "description": "Is the narrative neutral, avoiding opinions, and staying evidence-based?",
            "prompt": "Ensure the narrative is neutral, avoids opinions, and stays evidence-based. Check for any bias in the presentation.",
            "evaluation_approach": "Sentiment neutrality scoring and bias detection.",
            "max_score": 2,
            "scoring_logic": "2 = Neutral; 1 = Slightly biased; 0 = Biased"
        },
        "citation_quality": {
            "name": "Citation Quality",
            "description": "Are all sources valid, functional, and properly formatted?",
            "prompt": "Confirm that all sources are valid, functional, and properly formatted.",
            "evaluation_approach": "Link validation and citation parsing.",
            "max_score": 2,
            "scoring_logic": "2 = Verified; 1 = Partially valid; 0 = Broken/Missing"
        },
        "additional_readings_sec2": {
            "name": "Additional Readings",
            "description": "Are recommended similar cases or supplementary materials present?",
            "prompt": "Identify the presence of recommended similar cases or supplementary materials.",
            "evaluation_approach": "Scan for 'further reading' or 'reference' sections.",
            "max_score": 2,
            "scoring_logic": "2 = Present & comprehensive; 1 = Present but limited; 0 = Absent"
        }
    },
    "area3": {
        "learning_objectives_alignment": {
            "name": "Learning Objectives Alignment",
            "description": "Does case study content reflect and reinforce the teaching note's learning objectives?",
            "prompt": "Check if case study content reflects and reinforces the teaching note's learning objectives. Cross-map objective keywords between documents.",
            "evaluation_approach": "Textual cross-mapping of objective keywords.",
            "max_score": 3,
            "scoring_logic": "3 = Aligned; 2 = Partially aligned; 1 = Weakly aligned; 0 = Not aligned",
            "requires_teaching_note": True
        },
        "theories_frameworks": {
            "name": "Theories and Frameworks",
            "description": "Does the TN include relevant theoretical models connected to the case?",
            "prompt": "Ensure TN includes relevant theoretical models connected to the case (e.g., SWOT, 7S, etc.).",
            "evaluation_approach": "Detect framework references.",
            "max_score": 2,
            "scoring_logic": "2 = Present & used; 1 = Named but unused; 0 = Missing",
            "requires_teaching_note": True
        },
        "competency_alignment": {
            "name": "Competency Alignment",
            "description": "Are competencies from the Karmayogi Competency Model tagged and logically fit the case?",
            "prompt": "Verify tagging of competencies from the Karmayogi Competency Model, ensuring they logically fit the case. Match listed competencies with inferred behavioral indicators.",
            "evaluation_approach": "Match listed competencies with inferred behavioral indicators.",
            "max_score": 2,
            "scoring_logic": "2 = Strong alignment; 1 = Weak alignment; 0 = Absent",
            "requires_teaching_note": True
        },
        "sector_theme_sdg": {
            "name": "Sector/Theme Classification (SDG Linkage)",
            "description": "Is the case tagged to the correct sector or SDG theme?",
            "prompt": "Confirm correct tagging of the broader policy or thematic area and SDG linkage.",
            "evaluation_approach": "Semantic matching with pre-defined sector taxonomy.",
            "max_score": 2,
            "scoring_logic": "2 = Correct & comprehensive; 1 = Partially correct; 0 = Misclassified",
            "requires_teaching_note": True
        },
        "additional_readings_sec3": {
            "name": "Additional Readings (TN)",
            "description": "Are recommended similar cases or supplementary materials present in TN?",
            "prompt": "Identify the presence of recommended similar cases or supplementary materials in the Teaching Note.",
            "evaluation_approach": "Scan for 'further reading' or 'reference' sections in TN.",
            "max_score": 1,
            "scoring_logic": "1 = Present; 0 = Absent",
            "requires_teaching_note": True
        }
    },
    "area4": {
        "delivery_implementation_clarity": {
            "name": "Delivery & Implementation Clarity",
            "description": "Are challenges clearly articulated and solutions well explained?",
            "prompt": "Evaluate how challenges are articulated and whether solutions are well explained. Extract problem-solution pairs and measure clarity.",
            "evaluation_approach": "Extract problem-solution pairs and measure clarity score.",
            "max_score": 3,
            "scoring_logic": "3 = Clear; 2 = Partial; 1 = Incomplete; 0 = Ambiguous"
        },
        "protagonist_stakeholder": {
            "name": "Protagonist & Stakeholder Perspectives",
            "description": "Are perspectives of relevant stakeholders included and is the protagonist clearly identified?",
            "prompt": "Check if perspectives of relevant stakeholders are included and the protagonist is clearly identified.",
            "evaluation_approach": "Named-entity and role extraction, stakeholder mapping.",
            "max_score": 3,
            "scoring_logic": "3 = Clear protagonist & stakeholders; 2 = Partial coverage; 1 = Minimal; 0 = Missing"
        },
        "best_practices_lessons": {
            "name": "Best Practices & Lessons",
            "description": "Are lessons, replicable methods, or innovative practices clearly emerging from the narrative?",
            "prompt": "Identify lessons, replicable methods, or innovative practices clearly emerging from the narrative.",
            "evaluation_approach": "Keyword mapping and semantic clustering for 'best practice' phrases.",
            "max_score": 2,
            "scoring_logic": "2 = Evident; 1 = Weak; 0 = Missing"
        },
        "impact_visibility": {
            "name": "Impact Visibility",
            "description": "Are results, transformations, or measurable outcomes described and substantiated?",
            "prompt": "Determine whether results, transformations, or outcomes are described and substantiated.",
            "evaluation_approach": "Detection of outcome or results sections.",
            "max_score": 3,
            "scoring_logic": "3 = Visible & supported; 2 = Partial; 1 = Minimal; 0 = Absent"
        },
        "data_exhibits_quality": {
            "name": "Data and Exhibits Quality",
            "description": "Are data tables, figures, and exhibits relevant, clear, and sourced?",
            "prompt": "Assess whether data tables, figures, and exhibits are relevant, clear, and properly sourced.",
            "evaluation_approach": "Format detection and source mapping.",
            "max_score": 2,
            "scoring_logic": "2 = Strong; 1 = Needs improvement; 0 = Missing"
        }
    }
}

# Karmayogi Competency Model - Core competencies for case study mapping
KCM_COMPETENCIES = {
    "behavioral": {
        "integrity_ethics": {
            "name": "Integrity & Ethics",
            "description": "Adhering to high moral standards of honesty, integrity, and fairness in all actions."
        },
        "adaptability": {
            "name": "Adaptability",
            "description": "Recognizing that circumstances are dynamic and being willing to adjust approach as needed."
        },
        "compassion": {
            "name": "Compassion",
            "description": "Approaching work with a compassionate heart, considering the well-being and feelings of others."
        },
        "perpetual_learning": {
            "name": "Perpetual Learning",
            "description": "Always seeking to improve and grow, remaining open to new experiences, knowledge, and insights."
        },
        "commitment_purpose": {
            "name": "Commitment & Purpose",
            "description": "Performing duties with a profound sense of commitment and purpose, recognizing role in the larger scheme."
        },
        "inner_balance": {
            "name": "Inner Calm & Balance",
            "description": "Maintaining inner calm and balance regardless of success or failure."
        },
        "attention_detail": {
            "name": "Attention to Detail",
            "description": "Being fully present in the moment, giving complete attention to ensure utmost care and quality."
        }
    },
    "functional": {
        "citizen_centricity": {
            "name": "Citizen Centricity",
            "description": "Prioritizing Jana-Hita (citizen's well-being) and delivering efficient citizen-centric services."
        },
        "accountability": {
            "name": "Accountability",
            "description": "Being accountable to the citizens of the country with transparency and strong work ethic."
        },
        "innovation": {
            "name": "Innovation & Technology",
            "description": "Using technology to innovate and overcome challenges, encouraging entrepreneurial spirit."
        },
        "collaboration": {
            "name": "Collaboration & Unity",
            "description": "Working with collective resolve, promoting cooperative federation and strength in unity."
        },
        "strategic_thinking": {
            "name": "Strategic Thinking",
            "description": "Making decisions involving common good while focusing on factors of unity underlying national diversity."
        },
        "inclusive_development": {
            "name": "Inclusive Development",
            "description": "Promoting Sabka Saath, Sabka Vikas - inclusive economic and social development."
        },
        "cultural_awareness": {
            "name": "Cultural Awareness (Garva)",
            "description": "Pride in India's tangible and intangible heritage, promoting Indian Knowledge Systems."
        },
        "service_excellence": {
            "name": "Service Excellence",
            "description": "Striving for excellence in work and taking pride in providing the best service to citizens."
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
