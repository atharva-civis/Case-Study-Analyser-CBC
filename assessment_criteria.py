# Case Study Assessment Areas and Criteria
# Based on CBC-India AGK Case Study Review Rubric (Updated)

# Define the four main assessment areas with weights
ASSESSMENT_AREAS = {
    "area1": {
        "name": "Structure, Chronology & Logical Flow",
        "description": "Evaluates whether the case study is well-organised, follows a logical sequence, and maintains reader engagement.",
        "total_points": 12,
        "weight": 0.30
    },
    "area2": {
        "name": "Language, Citations & Factual Accuracy",
        "description": "Ensures the case study is readable, accurate, and meets editorial and academic standards.",
        "total_points": 14,
        "weight": 0.30
    },
    "area3": {
        "name": "Alignment with Teaching Note, Sector & Competencies",
        "description": "Checks whether the case and its teaching note complement each other and align with sectoral or competency goals.",
        "total_points": 6,
        "weight": 0.15
    },
    "area4": {
        "name": "Overall Effectiveness & Impact",
        "description": "Measures how well the case study achieves its intended educational and practical outcomes.",
        "total_points": 11,
        "weight": 0.25
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
            "max_score": 3,
            "scoring_logic": "3 = Clear sequential timeline; 2 = Sequential with minor gaps; 1 = Non-linear but understandable; 0 = Confusing"
        },
        "logical_coherence": {
            "name": "Logical Coherence",
            "description": "Do arguments and events build naturally upon each other?",
            "prompt": "Verify if arguments and events build naturally upon each other. Analyze paragraph transitions and causal flow.",
            "evaluation_approach": "Analyze paragraph transitions and causal flow.",
            "max_score": 3,
            "scoring_logic": "3 = Excellent flow; 2 = Consistent flow; 1 = Some gaps; 0 = Disjointed"
        },
        "sectional_connectivity": {
            "name": "Sectional Connectivity",
            "description": "Does each section connect smoothly with the previous one, maintaining a single narrative thread?",
            "prompt": "Ensure each section connects smoothly with the previous one, maintaining a single narrative thread.",
            "evaluation_approach": "Semantic linkage check between sections.",
            "max_score": 2,
            "scoring_logic": "2 = Connected; 1 = Partially connected; 0 = Fragmented"
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
            "max_score": 4,
            "scoring_logic": "4 = Excellent clarity & active voice; 3 = Clear & active; 2 = Minor issues; 1 = Wordy/Passive; 0 = Poor"
        },
        "factual_correctness": {
            "name": "Factual Correctness",
            "description": "Are all facts, data, and events verified with cited or linked evidence?",
            "prompt": "Verify all facts, data, and events with cited or linked evidence.",
            "evaluation_approach": "Cross-reference with cited sources or databases.",
            "max_score": 4,
            "scoring_logic": "4 = Fully accurate & well-documented; 3 = Accurate; 2 = Minor gaps; 1 = Questionable; 0 = Unverified"
        },
        "tone_neutrality_bias": {
            "name": "Tone Neutrality and Bias Check",
            "description": "Is the narrative neutral, avoiding opinions, and staying evidence-based?",
            "prompt": "Ensure the narrative is neutral, avoids opinions, and stays evidence-based. Check for any bias in the presentation.",
            "evaluation_approach": "Sentiment neutrality scoring and bias detection.",
            "max_score": 3,
            "scoring_logic": "3 = Completely neutral & evidence-based; 2 = Neutral; 1 = Slightly biased; 0 = Biased"
        },
        "citation_quality": {
            "name": "Citation Quality",
            "description": "Are all sources valid, functional, and properly formatted?",
            "prompt": "Confirm that all sources are valid, functional, and properly formatted.",
            "evaluation_approach": "Link validation and citation parsing.",
            "max_score": 3,
            "scoring_logic": "3 = All sources verified & well-formatted; 2 = Verified; 1 = Partially valid; 0 = Broken/Missing"
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
            "description": "Identifies competencies from the Karmayogi Competency Model that are relevant to the case and evaluates how well they fit.",
            "prompt": "Analyse the case study and teaching note to identify which competencies from the Karmayogi Competency Model (KCM) are relevant. Describe how the case narrative aligns with these competencies and whether the tagged competencies logically fit the case content. Provide a detailed narrative assessment.",
            "evaluation_approach": "Match listed competencies with inferred behavioral indicators.",
            "informational": True,
            "requires_teaching_note": True
        },
        "sector_theme_sdg": {
            "name": "Sector/Theme Classification & SDG Mapping",
            "description": "Identifies the relevant sector, thematic area, and Sustainable Development Goals (SDGs) linked to the case.",
            "prompt": "Analyse the case study and teaching note to identify: (1) the primary sector and thematic area the case belongs to, (2) relevant Sustainable Development Goals (SDGs) that the case addresses, and (3) how well the case content maps to these classifications. Provide a detailed narrative with specific SDG numbers and names.",
            "evaluation_approach": "Semantic matching with pre-defined sector taxonomy and SDG framework.",
            "informational": True,
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
        }
    }
}

# Karmayogi Competency Model - Core competencies and sub-competencies for case study mapping
KCM_COMPETENCIES = {
    "behavioral": {
        "integrity_ethics": {
            "name": "Integrity & Ethics",
            "description": "Adhering to high moral standards of honesty, integrity, and fairness in all actions.",
            "sub_competencies": ["Honesty", "Fairness", "Moral Courage", "Consistency", "Transparency"]
        },
        "adaptability": {
            "name": "Adaptability",
            "description": "Recognizing that circumstances are dynamic and being willing to adjust approach as needed.",
            "sub_competencies": ["Flexibility", "Openness to Change", "Resilience", "Versatility"]
        },
        "compassion": {
            "name": "Compassion",
            "description": "Approaching work with a compassionate heart, considering the well-being and feelings of others.",
            "sub_competencies": ["Empathy", "Sensitivity", "Kindness", "Supportive"]
        },
        "perpetual_learning": {
            "name": "Perpetual Learning",
            "description": "Always seeking to improve and grow, remaining open to new experiences, knowledge, and insights.",
            "sub_competencies": ["Self-Development", "Inquisitiveness", "Knowledge Sharing", "Reflective Practice"]
        },
        "commitment_purpose": {
            "name": "Commitment & Purpose",
            "description": "Performing duties with a profound sense of commitment and purpose, recognizing role in the larger scheme.",
            "sub_competencies": ["Dedication", "Goal Orientation", "Public Service Value", "Mission Focus"]
        },
        "inner_balance": {
            "name": "Inner Calm & Balance",
            "description": "Maintaining inner calm and balance regardless of success or failure.",
            "sub_competencies": ["Emotional Intelligence", "Stress Management", "Equanimity", "Self-Regulation"]
        },
        "attention_detail": {
            "name": "Attention to Detail",
            "description": "Being fully present in the moment, giving complete attention to ensure utmost care and quality.",
            "sub_competencies": ["Precision", "Thoroughness", "Meticulousness", "Quality Consciousness"]
        }
    },
    "functional": {
        "citizen_centricity": {
            "name": "Citizen Centricity",
            "description": "Prioritizing Jana-Hita (citizen's well-being) and delivering efficient citizen-centric services.",
            "sub_competencies": ["User-Centric Design", "Responsive Service", "Public Interest", "Service Delivery Focus"]
        },
        "accountability": {
            "name": "Accountability",
            "description": "Being accountable to the citizens of the country with transparency and strong work ethic.",
            "sub_competencies": ["Responsibility", "Transparency", "Results Orientation", "Ethical Governance"]
        },
        "innovation": {
            "name": "Innovation & Technology",
            "description": "Using technology to innovate and overcome challenges, encouraging entrepreneurial spirit.",
            "sub_competencies": ["Digital Literacy", "Creative Problem Solving", "Process Improvement", "Tech Adoption"]
        },
        "collaboration": {
            "name": "Collaboration & Unity",
            "description": "Working with collective resolve, promoting cooperative federation and strength in unity.",
            "sub_competencies": ["Teamwork", "Stakeholder Engagement", "Partnership Building", "Conflict Resolution"]
        },
        "strategic_thinking": {
            "name": "Strategic Thinking",
            "description": "Making decisions involving common good while focusing on factors of unity underlying national diversity.",
            "sub_competencies": ["Visionary Planning", "Systems Thinking", "Policy Analysis", "Risk Assessment"]
        },
        "inclusive_development": {
            "name": "Inclusive Development",
            "description": "Promoting Sabka Saath, Sabka Vikas - inclusive economic and social development.",
            "sub_competencies": ["Social Equity", "Diversity & Inclusion", "Sustainable Growth", "Poverty Alleviation"]
        },
        "cultural_awareness": {
            "name": "Cultural Awareness (Garva)",
            "description": "Pride in India's tangible and intangible heritage, promoting Indian Knowledge Systems.",
            "sub_competencies": ["Heritage Appreciation", "Local Context Awareness", "Indigenous Knowledge Support", "National Identity"]
        },
        "service_excellence": {
            "name": "Service Excellence",
            "description": "Striving for excellence in work and taking pride in providing the best service to citizens.",
            "sub_competencies": ["Standard Setting", "Efficiency", "Continuous Improvement", "Benchmarking"]
        }
    }
}

SECTOR_MAPPING = {
    "Agriculture": ["Horticulture", "Fertilizers", "Pest Control"],
    "Animal Husbandry and Fisheries": ["Fisheries", "Animal Husbandry", "Dairy"],
    "Commerce and Industries": ["MSME", "Manufacturing", "Marketing", "Business", "Commerce", "Entrepreneurship", "Startups", "Heavy Industry", "Steel", "Enterprises"],
    "Culture": ["Culture & Heritage"],
    "Defence": [],
    "Education": [],
    "Energy": ["Coal", "Natural Gas", "Non-Renewable Sources of Energy", "Petroleum", "Solar Energy", "Wind Energy"],
    "Engineering": ["Civil", "Electrical", "Mechanical"],
    "Environment": ["Forestry", "Waste Management", "Wildlife"],
    "External Affairs": ["Bilateral and Multilateral Relations", "Trade Negotiations", "Diplomatic Missions"],
    "Finance": ["Banking", "Budgeting", "Taxation", "Accounts", "Economics"],
    "Food Processing": [],
    "General Administration": ["Training", "Personnel Management", "Staff Officer", "Occupational Safety", "Revenue"],
    "Geology and Mining": [],
    "Governance": ["Public Administration", "Planning", "Scheme Delivery", "Grievance Redressal"],
    "Health and Nutrition": ["Drugs", "Public Health", "Nutrition"],
    "Home Affairs": ["Crime Control", "Enforcement, Vigilance", "Internal Security", "Intelligence Agency", "Law and Order", "Narcotics", "National Security", "Disaster Management", "Trafficking", "Paramilitary", "Civil Defence", "Cyber Control"],
    "Housing": [],
    "Information and Broadcasting": [],
    "Information Technology": ["e-Governance", "Cyber Security", "Artificial Intelligence", "Data", "Technology"],
    "Infrastructure": ["Ports", "Roads", "Shipping", "Aviation", "Transportation"],
    "Labour and Employment": [],
    "Land Resources": ["Sustainability"],
    "Law": [],
    "Marketing": [],
    "Postal Services": [],
    "Procurement": [],
    "Public Distribution System": [],
    "Public Policy": [],
    "Railways": [],
    "Rural Development/Panchayati Raj": ["Rural Management"],
    "Science & Technology": [],
    "Skill Development": ["Capacity Building", "Leadership", "Youth & Sports Affairs", "Citizen Centricity"],
    "Sports": [],
    "Space": [],
    "Telecommunications": ["Telecom Equipment", "Telecom Services", "Wireless Communication", "Satellite Communication", "Broadband Services", "Over-the-top Services"],
    "Textiles": [],
    "Tourism": [],
    "Urban Development": ["Smart City", "Urbanization"],
    "Water and Sanitation": [],
    "Welfare": ["Women and Child Development", "Poverty Alleviation", "Women Empowerment", "Social Justice", "Tribal Welfare", "Minority Affairs"],
}

PROMPT_EXCLUSION_INSTRUCTIONS = """
IMPORTANT EXCLUSION RULES — You MUST follow these when analysing the case study:
1. IGNORE the "Note from the Author" section entirely (author introductions, acknowledgements, author bios). Do NOT evaluate or consider this section in your analysis.
2. IGNORE the cover page content including any Creative Commons license references (e.g. http://creativecommons.org/licenses/by-nc-sa/4.0/), associated citation markers like [1], and any formatting issues related to these. Do NOT penalise or comment on these.
3. Begin your evaluation from the actual case study narrative content, skipping any prefatory/cover page material.
"""

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
        
        area_score = 0
        if area_id in assessment_results:
            for criterion_id, result in assessment_results[area_id].items():
                criteria_def = ASSESSMENT_CRITERIA.get(area_id, {}).get(criterion_id, {})
                if criteria_def.get("informational", False):
                    continue
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
