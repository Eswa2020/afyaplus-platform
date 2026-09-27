def break_even_requests(api_cost_per_req: float,
                        selfhost_fixed_monthly: float,
                        selfhost_var_per_req: float) -> float:
    # fixed + var*N = api*N  ->  N = fixed / (api - var)
    margin = api_cost_per_req - selfhost_var_per_req
    if margin <= 0:
        return float('inf')  # self-host never wins on unit cost
    return selfhost_fixed_monthly / margin

print(round(break_even_requests(0.000202, 1300.0, 0.00005), 0))