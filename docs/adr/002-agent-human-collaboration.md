# ADR-002: Agent-Human Collaboration Model

**Status:** Accepted
**Date:** 2024-01-15
**Deciders:** Platform Architecture Team, Operations Leadership

## Context

AI agents will make operational decisions about technician dispatch, warranty approvals, and parts procurement. These decisions have real business impact:

- Wrong dispatch wastes technician time and delays customer service
- Incorrect warranty denials lead to customer dissatisfaction and disputes
- Parts over-ordering ties up capital; under-ordering causes service delays

The system must balance automation efficiency with human judgment and accountability.

## Decision

We implement a "recommend and approve" collaboration model where:

1. **Agents recommend, humans decide**: Every agent decision starts in "pending" status requiring human approval.
2. **Confidence-based routing**: High-confidence decisions (>90%) can be auto-approved in production (configurable threshold).
3. **Override capability**: Humans can override any decision with documented reasoning.
4. **Full audit trail**: Every decision logged with agent reasoning, confidence score, and human action.
5. **Feedback loop**: Overrides inform future agent improvements (manual process initially).

## Rationale

**This model provides:**

- **Safety**: No agent decision executes without human visibility.
- **Learning**: Operators see agent reasoning and build trust over time.
- **Flexibility**: Confidence thresholds adjust as agents improve.
- **Accountability**: Clear audit trail for compliance and disputes.
- **Gradual rollout**: Start with manual approval, move to auto-approval for proven decisions.

**Alternatives Considered:**

1. **Fully autonomous agents**: Agents execute decisions automatically without human approval.
   - **Rejected**: Too risky for production. One bad decision could delay critical service or approve fraudulent warranty claims.

2. **Humans-only with agent suggestions**: Agents provide information but humans make all decisions manually.
   - **Rejected**: Loses automation benefits. Operators drown in information without clear recommendations.

3. **Approval by exception**: Auto-execute unless flagged for review.
   - **Rejected**: Operators miss learning opportunities and may not catch issues until too late.

4. **Voting ensemble**: Multiple agents vote, humans break ties.
   - **Rejected**: Over-engineered for current scope. Single agents with confidence scores provide sufficient signal.

## Implementation Details

**Base Agent Contract:**

Every agent implements:
```python
async def execute(
    entity_id: UUID,
    entity_type: str,
    context: dict[str, Any],
    db: AsyncSession,
) -> AgentDecision
```

Returns `AgentDecision` with:
- `reasoning`: Plain language explanation
- `confidence_score`: Float between 0 and 1
- `recommendation`: Structured data for action
- `status`: "pending" by default

**Human Actions:**

Operators can:
- **Approve**: `POST /api/decisions/{id}/approve`
- **Override**: `POST /api/decisions/{id}/override` with reason

**Audit Trail:**

Database stores:
- Timestamp of agent decision
- Agent name and version
- Full reasoning and confidence
- Human action (approve/override)
- Override reason if applicable
- User who took action

## Consequences

**Positive:**
- Operators learn agent reasoning patterns
- Clear accountability for every decision
- Gradual trust building as agents prove reliability
- Full compliance audit trail
- Easy rollback if agents make errors

**Negative:**
- Manual approval adds latency to decisions
- Operators may rubber-stamp without reading reasoning
- Need UI that surfaces agent reasoning clearly
- Confidence thresholds require tuning over time

**Mitigation:**
- Dashboard shows reasoning prominently before approve button
- Track approval time to identify rubber-stamping
- Start with 100% manual approval, collect metrics, then tune thresholds
- Weekly review of overrides to improve agents

## Transition Plan

**Phase 1 (Weeks 1-4): Full Manual Approval**
- All decisions require human approval
- Collect baseline metrics on approval rate, override rate, decision quality

**Phase 2 (Weeks 5-8): Confidence-Based Routing**
- Auto-approve decisions >95% confidence for low-stakes categories (parts procurement)
- Continue manual approval for high-stakes (dispatch, warranty)

**Phase 3 (Weeks 9-12): Expanded Automation**
- Lower threshold to 90% for proven categories
- Expand auto-approval to medium-stakes decisions
- Maintain human review for edge cases

**Phase 4 (Month 4+): Continuous Improvement**
- Analyze override patterns
- Retrain agents on common override scenarios
- Adjust confidence thresholds per category

## Validation

Success criteria:
- <5% override rate after 30 days of manual approval
- <10 seconds average time from decision to approval
- 100% of decisions have audit trail
- Zero data loss on overrides

## References

- Human-in-the-loop AI patterns: https://hai.stanford.edu/news/humans-loop-design-interactive-ai-systems
- MLOps best practices for production AI
