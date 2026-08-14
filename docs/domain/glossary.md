# Field Service Domain Glossary

This document defines key terms and concepts in the field service domain as implemented in this platform.

## Service Operations

### Service Ticket
A work order created when a customer requests service. Each ticket contains:
- **Title and Description**: What work needs to be done
- **Service Type**: Category of work (preventive maintenance, breakdown, installation, callback, inspection)
- **Priority**: Urgency level (critical, high, medium, low)
- **Status**: Current state (open, assigned, in_progress, completed, cancelled, on_hold)
- **Location**: Customer site address and coordinates
- **Required Skills**: Technical capabilities needed to complete the work
- **Estimated Duration**: Expected time to complete in hours

### Technician
A field service worker who performs on-site service work. Technicians have:
- **Skills**: Technical capabilities with proficiency levels (basic, intermediate, advanced, expert)
- **Home Location**: Starting point for route calculations
- **Current Location**: Real-time position (when available)
- **Availability**: Whether currently available for assignments
- **Max Jobs Per Day**: Capacity limit for workload management

### Dispatch
The process of assigning a service ticket to a technician. Considers:
- Skill matching between ticket requirements and technician capabilities
- Proximity (distance from technician to job site)
- Current workload and capacity
- Scheduled appointments and availability

## Warranty Management

### Warranty Claim
A request for warranty coverage on a failed product or component. Contains:
- **Product Information**: Serial number and model
- **Purchase Date**: When customer acquired the product
- **Warranty End Date**: When coverage expires
- **Failure Date**: When the issue occurred
- **Failure Description**: What went wrong
- **Estimated Cost**: Repair or replacement cost

### Warranty Status
Current state of a claim:
- **Pending**: Awaiting review
- **Approved**: Coverage granted, work can proceed
- **Rejected**: Not covered under warranty terms
- **Expired**: Claim filed after warranty period ended
- **Disputed**: Customer contests rejection

### Coverage Percentage
Portion of repair cost covered by warranty (0-100%). May be partial if:
- Claim is near warranty expiration
- Failure cause is partially customer responsibility
- Depreciation applies to older products

## Parts and Inventory

### Part
A component or consumable used in service work. Each part has:
- **Part Number**: Unique identifier
- **Category**: Type of component (mechanical, electrical, hydraulic, etc.)
- **Quantity in Stock**: Current inventory level
- **Reorder Point**: Stock level that triggers procurement
- **Reorder Quantity**: Amount to order when restocking
- **Unit Price**: Cost per item
- **Vendor Information**: Supplier name and lead time

### Part Status
Current inventory state:
- **In Stock**: Adequate inventory available
- **Low Stock**: Below reorder point, procurement needed
- **Out of Stock**: Zero inventory, urgent procurement needed
- **On Order**: Procurement in progress
- **Discontinued**: No longer available

### Procurement
The process of ordering parts from vendors. Considers:
- Stock levels versus reorder points
- Historical usage patterns
- Vendor lead times
- Cost optimization
- Urgency based on current service needs

## Agent Decisions

### Agent Decision
A recommendation made by an AI agent with:
- **Agent Name**: Which agent made the decision
- **Decision Type**: Category of decision (technician_assignment, warranty_assessment, parts_procurement)
- **Entity**: What the decision applies to (ticket, claim, part)
- **Reasoning**: Plain language explanation of why this recommendation was made
- **Confidence Score**: Agent's certainty (0.0 to 1.0, where 1.0 is highest confidence)
- **Recommendation**: Structured data containing the suggested action
- **Status**: Current state (pending, approved, rejected, overridden)

### Confidence Score
A number between 0 and 1 indicating how certain the agent is about its recommendation:
- **0.90-1.00**: Very high confidence, strong evidence supports recommendation
- **0.75-0.89**: High confidence, recommendation likely correct
- **0.60-0.74**: Moderate confidence, recommendation reasonable but uncertain
- **0.00-0.59**: Low confidence, manual review strongly recommended

### Human Override
When an operator rejects an agent recommendation and chooses a different action:
- **Override Reason**: Why the agent was wrong
- **Overridden By**: User who made the override
- **New Values**: What the operator chose instead

This feedback helps improve agent reasoning over time.

## Operational Metrics

### Response Time
Time from ticket creation to technician assignment. Key performance indicator for dispatch efficiency.

### First Call Resolution
Percentage of tickets completed on the first visit without callbacks. Indicates effective diagnosis and parts availability.

### SLA Compliance
Percentage of tickets resolved within service level agreement timeframes. Varies by priority level:
- Critical: 4 hours
- High: 8 hours
- Medium: 24 hours
- Low: 48 hours

### Technician Utilization
Percentage of available work hours spent on productive service tasks (excludes travel, breaks, training).

### Warranty Approval Rate
Percentage of warranty claims approved. Monitors for trends indicating product quality issues.

### Stock-Out Rate
Percentage of service tickets delayed due to parts unavailability. Target: zero for critical parts.

## Service Types

### Preventive Maintenance
Scheduled inspections and maintenance to prevent breakdowns. Typically planned weeks in advance.

### Breakdown
Emergency service when equipment fails unexpectedly. Highest priority, requires rapid dispatch.

### Installation
Deploying new equipment at customer site. Requires specialized skills and often multiple technicians.

### Callback
Return visit to address issues from a previous service call. May indicate incomplete initial repair.

### Inspection
Safety or compliance check without repair work. Common for elevators and regulated equipment.

## Skill Categories

### Mechanical
Physical repair and adjustment skills: elevator mechanics, hydraulic systems, cable replacement.

### Electrical
Power systems, control wiring, sensor installation.

### Electronics
Circuit boards, programmable controllers, diagnostic systems.

### Safety Compliance
Regulatory knowledge for inspections, code compliance, safety certifications.

### Diagnostics
Troubleshooting and root cause analysis.

### Modernization
Upgrading legacy systems with new technology.

## Risk Factors

Conditions that affect warranty coverage or service complexity:

### Warranty Risk Factors
- Expired warranty period
- Exclusion keywords (water damage, abuse, unauthorized modification)
- Delayed claim filing
- Inconsistent failure description

### Service Risk Factors
- Remote location (long travel time)
- After-hours service requirement
- Specialized skills needed
- Parts availability uncertain
- Multi-technician coordination required

## Related Documentation

- [Architecture Decision Records](../adr/)
- [API Documentation](http://localhost:8000/docs)
- [Local Setup Guide](../runbooks/local-setup.md)
