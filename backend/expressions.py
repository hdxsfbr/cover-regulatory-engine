"""Finite, unit-checked expression trees; no eval or generated Python."""

import math

UNITS = {"scalar": 0, "ft": 1, "sq ft": 2, "%": 0, "bool": None}


def evaluate(node, inputs, depth=0):
    if depth > 24 or not isinstance(node, dict):
        raise ValueError("Invalid expression tree")
    op = node.get("op")
    if op in ("constant", "input"):
        unit = node.get("unit")
        value = node.get("value") if op == "constant" else inputs.get(node.get("name"))
        if (
            unit not in UNITS
            or type(value) not in (int, float, bool)
            or (unit == "bool") != (type(value) is bool)
            or not math.isfinite(value)
        ):
            raise ValueError("Invalid or missing typed operand")
        return value, unit
    args = node.get("args")
    if not isinstance(args, list) or not 1 <= len(args) <= 8:
        raise ValueError("Invalid operands")
    values = [evaluate(a, inputs, depth + 1) for a in args]
    nums = [v[0] for v in values]
    units = [v[1] for v in values]
    if op == "if" and len(values) == 3:
        if units[0] != "bool" or units[1] != units[2]:
            raise ValueError("Invalid conditional units")
        return values[1] if nums[0] else values[2]
    if op in ("lt", "lte", "eq") and len(values) == 2:
        if units[0] != units[1]:
            raise ValueError("Comparison unit mismatch")
        return {
            "lt": lambda: nums[0] < nums[1],
            "lte": lambda: nums[0] <= nums[1],
            "eq": lambda: nums[0] == nums[1],
        }[op](), "bool"
    if "bool" in units:
        raise ValueError("Boolean arithmetic forbidden")
    if op in ("min", "max", "add", "subtract"):
        if len(set(units)) != 1 or (op == "subtract" and len(values) != 2):
            raise ValueError("Arithmetic unit mismatch")
        value = (
            min(nums)
            if op == "min"
            else max(nums)
            if op == "max"
            else sum(nums)
            if op == "add"
            else nums[0] - nums[1]
        )
        unit = units[0]
    elif op in ("multiply", "divide") and len(values) == 2:
        power = UNITS[units[0]] + (
            UNITS[units[1]] if op == "multiply" else -UNITS[units[1]]
        )
        if power not in (0, 1, 2) or (op == "divide" and nums[1] == 0):
            raise ValueError("Invalid dimensional arithmetic")
        value = nums[0] * nums[1] if op == "multiply" else nums[0] / nums[1]
        unit = {0: "scalar", 1: "ft", 2: "sq ft"}[power]
    elif op == "ceil" and len(values) == 1 and units[0] == "scalar":
        value, unit = math.ceil(nums[0]), "scalar"
    else:
        raise ValueError("Unsupported expression operation")
    if not math.isfinite(value):
        raise ValueError("Non-finite expression result")
    return value, unit


def describe(node):
    op = node["op"]
    if op == "constant":
        return str(node["value"]) + (
            " " + node["unit"] if node["unit"] not in ("scalar", "bool") else ""
        )
    if op == "input":
        return (
            node["name"]
            .replace("_sqft", "")
            .replace("_ft", "")
            .replace("_percent", "")
            .replace("_", " ")
        )
    args = [describe(n) for n in node["args"]]
    if op == "if":
        return f"If {args[0]}: {args[1]}; otherwise {args[2]}"
    symbols = {
        "multiply": " × ",
        "divide": " ÷ ",
        "add": " + ",
        "subtract": " − ",
        "lt": " < ",
        "lte": " ≤ ",
        "eq": " = ",
    }
    if op in symbols:
        return "(" + symbols[op].join(args) + ")"
    return op + "(" + ", ".join(args) + ")"
