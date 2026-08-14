# ADR-003: Integration Architecture

**Status:** Accepted
**Date:** 2024-01-15
**Deciders:** Platform Architecture Team

## Context

The field service platform must integrate with external systems:

- **Calendar systems** (Google Calendar, Outlook) for technician scheduling
- **CRM systems** (Salesforce, HubSpot) for customer data
- **Inventory systems** (SAP, NetSuite) for parts availability
- **Mapping services** (Google Maps, Mapbox) for route optimization
- **Notification services** (Twilio, SendGrid) for customer updates

Integration requirements:
- Support multiple vendors per category (not all customers use same CRM)
- Graceful degradation if external service is unavailable
- Mock implementations for development and demos
- Extensible architecture for adding new integrations
- Secure credential management

## Decision

We implement a **plugin-based integration layer** with:

1. **Model Context Protocol (MCP) client** for standardized external tool access
2. **Adapter pattern** for each integration category (Calendar, CRM, Inventory, etc.)
3. **Mock implementations** that satisfy adapter interfaces for demo mode
4. **Configuration-driven selection** of which implementation to use
5. **Circuit breaker pattern** for external service resilience

## Rationale

**MCP provides:**
- Standardized protocol for LLM-tool interactions
- Growing ecosystem of pre-built integrations
- Clear separation between agent logic and external calls
- Easy to swap implementations without changing agent code

**Adapter pattern provides:**
- Interface consistency across vendors
- Easy testing with mock implementations
- Clear contract for adding new integrations

**Circuit breaker provides:**
- Resilience when external services fail
- Automatic retry with exponential backoff
- Metrics on integration health

**Alternatives Considered:**

1. **Direct API calls in agent code**: Agents call external APIs directly.
   - **Rejected**: Tight coupling makes testing hard and vendor switching painful.

2. **GraphQL federation**: Federated graph across all external systems.
   - **Rejected**: Over-engineered for current scope. Many external systems don't provide GraphQL.

3. **Enterprise service bus (ESB)**: Central message bus for all integrations.
   - **Rejected**: Heavy infrastructure overhead. Async messaging not needed for synchronous agent decisions.

4. **Zapier/Make webhooks**: Use no-code tools for integrations.
   - **Rejected**: Limited control over error handling and retry logic. Not suitable for production reliability.

## Implementation Details

**Integration Layer Structure:**

```
packages/integrations/
├── base.py              # Base adapter interfaces
├── calendar/
│   ├── base.py         # CalendarAdapter interface
│   ├── google.py       # Google Calendar implementation
│   ├── outlook.py      # Outlook implementation
│   └── mock.py         # Mock for development
├── crm/
│   ├── base.py         # CRMAdapter interface
│   ├── salesforce.py   # Salesforce implementation
│   └── mock.py         # Mock for development
└── inventory/
    ├── base.py         # InventoryAdapter interface
    ├── sap.py          # SAP implementation
    └── mock.py         # Mock for development
```

**Adapter Interface Example:**

```python
class CalendarAdapter(ABC):
    @abstractmethod
    async def get_availability(
        self, technician_id: str, date_range: tuple[datetime, datetime]
    ) -> list[TimeSlot]:
        """Get technician availability for date range."""
        pass

    @abstractmethod
    async def create_event(
        self, technician_id: str, event: CalendarEvent
    ) -> str:
        """Create calendar event, return event ID."""
        pass
```

**Configuration:**

```python
# .env
CALENDAR_INTEGRATION=google  # or outlook, or mock
CRM_INTEGRATION=salesforce   # or hubspot, or mock
INVENTORY_INTEGRATION=sap    # or netsuite, or mock
```

**Factory Pattern:**

```python
def get_calendar_adapter() -> CalendarAdapter:
    integration_type = settings.calendar_integration
    if integration_type == "google":
        return GoogleCalendarAdapter()
    elif integration_type == "outlook":
        return OutlookCalendarAdapter()
    else:
        return MockCalendarAdapter()
```

**Mock Implementation:**

Mock adapters return realistic demo data without external dependencies:

```python
class MockCalendarAdapter(CalendarAdapter):
    async def get_availability(
        self, technician_id: str, date_range: tuple[datetime, datetime]
    ) -> list[TimeSlot]:
        # Return simulated availability
        return [
            TimeSlot(start=..., end=..., is_available=True),
            # More slots...
        ]
```

## Consequences

**Positive:**
- Easy development without real external services (use mocks)
- Testable in CI/CD without external dependencies
- Swap vendors without changing agent code
- Clear interface contracts prevent integration drift
- Demo mode works anywhere (no API keys needed)

**Negative:**
- More upfront code to define adapter interfaces
- Need to maintain mock implementations in sync with real ones
- Factory pattern adds indirection
- Each new vendor requires adapter implementation

**Mitigation:**
- Start with mock adapters to validate interfaces before implementing real ones
- Integration tests validate real adapter implementations
- Document adapter interface thoroughly
- Use type hints to catch interface mismatches early

## Security Considerations

**Credential Management:**
- Store API keys in environment variables or secret manager (AWS Secrets Manager, HashiCorp Vault)
- Never commit credentials to repository
- Rotate credentials periodically
- Use least-privilege API scopes

**Data Privacy:**
- Only fetch minimum required data from external systems
- Do not store sensitive customer data unnecessarily
- Audit all external API calls
- Respect data retention policies

## Validation

Success criteria:
- Agents function identically whether using mock or real integrations
- Mock implementations sufficient for demos and development
- New integration adapter implemented in <1 week
- Zero credential leaks in repository or logs

## Future Enhancements

1. **MCP server implementations**: Build custom MCP servers for proprietary systems.
2. **Integration health dashboard**: Monitor external service availability and latency.
3. **Retry policies per vendor**: Different backoff strategies for different APIs.
4. **Rate limiting**: Respect external API rate limits automatically.

## References

- Model Context Protocol: https://modelcontextprotocol.io
- Circuit breaker pattern: https://microservices.io/patterns/reliability/circuit-breaker.html
- Adapter pattern: https://refactoring.guru/design-patterns/adapter
