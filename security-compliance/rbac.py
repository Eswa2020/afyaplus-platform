"""Application-level authorisation: which role may call which MCP tool."""
TOOLS_BY_ROLE = {
    'partner_clinic': {'check_stock'},
    'clinical_ops': {'check_stock', 'plan_delivery_route'},
}


def allowed(role: str, tool: str) -> bool:
    return tool in TOOLS_BY_ROLE.get(role, set())


if __name__ == '__main__':
    assert allowed('partner_clinic', 'check_stock') is True
    assert allowed('clinical_ops', 'plan_delivery_route') is True
    # A partner must never reach the routing tool
    assert allowed('partner_clinic', 'plan_delivery_route') is False
    # An unknown role is a denial, not a KeyError
    assert allowed('intern', 'check_stock') is False
    # dump_all is absent from the matrix, so it is denied to everybody
    assert not any(allowed(r, 'dump_all') for r in TOOLS_BY_ROLE)
    print('rbac OK', len(TOOLS_BY_ROLE), 'roles, deny-by-default holds')