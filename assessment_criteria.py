# Assessment Areas and Criteria based on the provided information

# Define the three main assessment areas
ASSESSMENT_AREAS = {
    "area1": {
        "name": "Does the Draft Clearly Explain Why and What?",
        "description": "This area evaluates how well the policy document explains its purpose, objectives, and structure."
    },
    "area2": {
        "name": "Does the Draft Thoroughly Assess the Impact?",
        "description": "This area evaluates the depth and breadth of impact analysis in the policy document."
    },
    "area3": {
        "name": "Does the Draft Enable Meaningful Public Participation?",
        "description": "This area evaluates how well the policy enables and encourages public feedback and participation."
    }
}

# Define the specific criteria for each assessment area
ASSESSMENT_CRITERIA = {
    "area1": {
        "justification": {
            "name": "Justification",
            "description": "Is the need for the policy well-founded? Does the policy provide relevant context, data, or rationale for why it is needed?"
        },
        "essential_elements": {
            "name": "Essential Elements",
            "description": "Are the main objectives, provisions, or changes the policy introduces clearly stated? Does it specify what the policy aims to achieve?"
        },
        "comprehension": {
            "name": "Comprehension",
            "description": "Is the policy text accessible, logically structured, and free of contradictions? Does it use clear language, headings, or summaries that aid understanding?"
        }
    },
    "area2": {
        "problem_identification": {
            "name": "Problem Identification",
            "description": "Does the policy define the root cause or specific issue it aims to address? Are challenges or market failures clearly outlined?"
        },
        "evidence": {
            "name": "Evidence for the Problem",
            "description": "Does the policy provide data, research, or statistics to illustrate the problem? Are references or external studies cited?"
        },
        "cost_benefit": {
            "name": "Cost-Benefit Analysis",
            "description": "Does the policy include an economic or financial appraisal of its measures? Does it weigh potential benefits against costs or risks?"
        },
        "alternatives": {
            "name": "Alternatives",
            "description": "Does the draft discuss other policy models or approaches? Is there a reason the chosen approach is deemed preferable?"
        },
        "stakeholder_impacts": {
            "name": "Stakeholder Impacts",
            "description": "How does the policy affect regulated entities, intended beneficiaries, and indirect stakeholders like communities or supply-chain actors?"
        },
        "environmental": {
            "name": "Environmental Considerations",
            "description": "Does the policy mention potential environmental impacts? Does it provide mitigation measures?"
        },
        "timeframes": {
            "name": "Time Frames",
            "description": "Are there clear timelines for implementation or achieving policy goals? Does it distinguish between short-, medium-, and long-term impacts?"
        },
        "evaluation": {
            "name": "Continuous Evaluation",
            "description": "Is there a mechanism for ongoing monitoring or iterative review? Are oversight committees or annual reporting procedures mentioned?"
        },
        "territorial": {
            "name": "Territorial Impact",
            "description": "Does the policy address geographic considerations (rural vs. urban, different zones or clusters)? Are regional disparities or localized impacts accounted for?"
        }
    },
    "area3": {
        "consultation_duration": {
            "name": "Consultation Duration",
            "description": "Is there a defined window (e.g., 30 days) for public feedback? Does the policy specify timelines or deadlines for submitting comments?"
        },
        "feedback_collection": {
            "name": "Feedback Collection",
            "description": "Are there multiple avenues for providing feedback (online, offline, in-person)? Does the policy specify how feedback will be gathered, documented, or addressed?"
        },
        "translations": {
            "name": "Translations",
            "description": "Does the policy mention translations into local/regional languages? Are accessibility measures for disabled or non-English-speaking stakeholders discussed?"
        }
    }
}
