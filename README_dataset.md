# Project Multi-Agent Issue Resolution Dataset

## Overview
This dataset contains 20,000 realistic project management communication records designed for building a RAG-based multi-agent system to generate issue resolution options.

**Based on**: Project requirements from slide 11 of kick-off-v2.pdf
**Project**: Multi-agent system to evaluate and generate issue resolution options
**Use Case**: Training agentic RAG systems (Mail Agent, ProjectPlan Agent, Schedule Meeting Agent)

## Dataset Characteristics

- **Total Records**: 20,000
- **Unique Projects**: 13,577
- **Unique Issues**: 15,058
- **Issue Types**: 15 categories
- **Time Range**: Last 6 months of project communications
- **Resolution Rate**: ~35% resolved, 65% pending decision
- **Follow-up Rate**: ~25% are follow-up communications on existing issues

## Key Features for RAG System

### 1. Issue Tracking Across Communications
- Issues can have multiple communications (tracked via `issue_id` and `communication_sequence`)
- ~25% of records are follow-ups, enabling the system to learn context accumulation
- Previous communications stored in JSON format for context retrieval

### 2. Multi-Category Issue Classification
15 realistic project issue types:
- Schedule Delay
- Resource Constraint
- Budget Overrun
- Technical Challenge
- Scope Creep
- Quality Issue
- Communication Gap
- Dependency Block
- Risk Materialization
- Stakeholder Conflict
- Requirements Change
- Integration Problem
- Performance Issue
- Security Concern
- Compliance Issue

### 3. Contextual Resolution Options
Each issue includes 2-4 resolution options categorized by strategy:
- `accept_delay` - Accepting timeline adjustments
- `reject_implications_severe` - Rejecting due to critical impact
- `need_more_info` - Requesting additional information
- `add_resources` - Increasing team capacity
- `reduce_scope` - Descoping features
- `parallel_work` - Reorganizing workflows
- `technical_solution` - Technical alternatives
- `budget_increase` - Requesting additional funds
- `risk_mitigation` - Implementing risk strategies
- `stakeholder_negotiation` - Negotiating with stakeholders

### 4. Real-World Project Context
- 15 project domains (Software Dev, Construction, Cloud Migration, AI/ML, etc.)
- 12 project phases (Planning, Design, Development, Testing, etc.)
- 4 severity levels (Low, Medium, High, Critical)
- 14 sender roles (PM, Tech Lead, Developer, Stakeholder, etc.)
- 5 communication types (Email, Slack, Teams, Meeting Notes, Status Updates)

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `record_id` | int | Unique identifier for each record |
| `project_id` | string | Project identifier (e.g., PROJ-1234) |
| `issue_id` | string | Issue identifier (e.g., PROJ-1234-567) |
| `communication_sequence` | int | Communication sequence number (1, 2, 3...) |
| `is_follow_up` | bool | Whether this is a follow-up communication |
| `issue_type` | string | Category of issue (15 types) |
| `issue_category` | string | Same as issue_type |
| `project_domain` | string | Project domain/industry |
| `project_phase` | string | Current project phase |
| `severity` | string | Low/Medium/High/Critical |
| `communication_type` | string | Communication medium |
| `sender_role` | string | Role of sender |
| `communication_timestamp` | datetime | When communication occurred |
| `issue_description` | string | Detailed issue description |
| `previous_communications` | JSON | Array of previous communications (if any) |
| `has_previous_context` | bool | Whether previous context exists |
| `resolution_options` | JSON | Array of 2-4 resolution options |
| `num_resolution_options` | int | Number of resolution options |
| `is_resolved` | bool | Whether issue is resolved |
| `chosen_resolution_option` | int | Which option was chosen (1-4 or null) |
| `days_since_reported` | int | Days since first report |
| `urgency_level` | string | Urgency classification |

## JSON Structures

### previous_communications
```json
[
  {
    "comm_date": "2025-11-15",
    "summary": "Initial issue reported by team member"
  },
  {
    "comm_date": "2025-11-17",
    "summary": "Follow-up on status and impact assessment"
  }
]
```

### resolution_options
```json
[
  {
    "option_id": 1,
    "option_text": "Accept the delay and adjust project timeline accordingly...",
    "option_category": "accept_delay"
  },
  {
    "option_id": 2,
    "option_text": "Cannot accept delay. Critical business deadline non-negotiable...",
    "option_category": "reject_implications_severe"
  }
]
```

## Usage for Multi-Agent RAG System

### 1. Training Data Preparation
```python
# Load dataset
import pandas as pd
df = pd.read_csv('project_multiagent_issue_resolution_dataset_20k.csv')

# Filter for resolved issues (training labels)
resolved_issues = df[df['is_resolved'] == True]

# Extract text for embedding
texts = df['issue_description'].tolist()
```

### 2. RAG Vector Store Construction
```python
# Create embeddings for issue descriptions
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(texts, embeddings)
```

### 3. Context Retrieval for Similar Issues
```python
# When new issue arrives, retrieve similar past issues
def get_similar_issues(new_issue_description, k=5):
    similar = vectorstore.similarity_search(new_issue_description, k=k)
    return similar
```

### 4. Multi-Agent Resolution Generation
Based on slide 11 architecture:

**Mail Agent**: Analyzes incoming communication
```python
# Extract issue details from communication
issue_type = classify_issue(email_content)
severity = assess_severity(email_content)
```

**ProjectPlan Agent**: Evaluates project context
```python
# Check if issue known from previous communications
previous_context = df[df['issue_id'] == current_issue_id]['previous_communications']
```

**Schedule Meeting Agent**: Determines if meeting needed
```python
# Check resolution options that require meetings
meeting_required = any('meeting' in opt['option_text'].lower() 
                      for opt in resolution_options)
```

### 5. Resolution Option Evaluation
```python
# Generate resolution options based on:
# 1. Similar historical issues
# 2. Issue type and severity
# 3. Previous communication context

def generate_resolution_options(issue):
    similar_issues = get_similar_issues(issue['description'])

    # Extract successful resolution patterns
    successful_resolutions = [
        si['chosen_resolution_option'] 
        for si in similar_issues 
        if si['is_resolved']
    ]

    # Generate 2-4 options based on patterns
    return evaluate_and_rank_options(successful_resolutions, issue)
```

## Data Quality Features

✓ **Realistic Scenarios**: Based on actual project management patterns and common issues
✓ **Temporal Consistency**: Timestamp distribution over 6 months
✓ **Issue Tracking**: Problems tracked across multiple communications (as per slide 11 requirement)
✓ **Resolution Patterns**: Options aligned with real-world project management strategies
✓ **Domain Diversity**: 15 different project domains for generalization
✓ **Severity Distribution**: Realistic distribution (35% Medium, 30% High, 25% Low, 10% Critical)

## Model Training Recommendations

### For Classification Task
- **Input**: `issue_description`, `project_domain`, `project_phase`, `severity`
- **Output**: `issue_type`
- **Model**: BERT-based classifier or GPT fine-tuning

### For Resolution Generation
- **Input**: `issue_description` + `previous_communications` + `project_context`
- **Output**: `resolution_options` (2-4 options)
- **Model**: RAG with GPT-4 or Claude

### For Resolution Selection
- **Input**: `issue_description` + `resolution_options` + `historical_outcomes`
- **Output**: `chosen_resolution_option`
- **Model**: Ranking model or multi-agent decision system

## Evaluation Metrics

For the multi-agent RAG system, consider:
- **Retrieval Accuracy**: Are similar historical issues retrieved?
- **Option Relevance**: Do generated options match issue type patterns?
- **Option Diversity**: Are different resolution strategies represented?
- **Context Utilization**: Is previous communication context used effectively?
- **Decision Quality**: For resolved issues, was the chosen option appropriate?

## Example Queries for RAG System

1. **Finding similar past issues**:
   - "Schedule delay in testing phase for software development project"

2. **Checking previous communications**:
   - Filter by `issue_id` and sort by `communication_sequence`

3. **Pattern mining for resolution strategies**:
   - Group by `issue_type` + `chosen_resolution_option`

4. **Context-aware retrieval**:
   - Search by `issue_description` + filter by `project_domain` and `severity`

## Limitations & Future Enhancements

**Current Limitations**:
- Synthetic data (though based on real patterns)
- No actual email text (only structured descriptions)
- Limited project-specific context

**Potential Enhancements**:
- Add full email text and conversation threads
- Include project plan details and constraints
- Add stakeholder profiles and preferences
- Include actual resolution outcomes and effectiveness metrics
- Add cost and timeline impact data

## Citation

If you use this dataset, please cite the source project:
- Project: Multi-agent Issue Resolution System
- Based on: AIcoo Project Management Automation
- Dataset Version: 1.0
- Generated: November 2025

## License

This dataset is generated for research and educational purposes.
