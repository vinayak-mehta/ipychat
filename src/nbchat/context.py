# -*- coding: utf-8 -*-

import ast
import inspect
from typing import Any, Dict, Optional


def extract_variables_from_query(query: str) -> set:
    """Extract potential variable names from the query string."""
    words = set(query.split())
    return words


def get_variable_info(name: str, value: Any) -> str:
    """Get detailed information about a variable."""
    info_parts = [f"Variable: {name}"]
    info_parts.append(f"Type: {type(value).__name__}")

    # dataframes
    if "pandas.core.frame.DataFrame" in str(type(value)):
        info_parts.append(f"Shape: {value.shape}")
        info_parts.append("Columns:")
        for col in value.columns:
            info_parts.append(f"- {col} ({value[col].dtype})")
        info_parts.append("\nSample (first 5 rows):")
        info_parts.append(str(value.head()))

    # functions
    elif inspect.isfunction(value):
        info = [
            f"Variable: {name}",
            "Type: function",
            f"Documentation: {inspect.getdoc(value)}"
            if inspect.getdoc(value)
            else None,
            "Source code:",
            inspect.getsource(value),
        ]
        return "\n".join(filter(None, info))

    # objects
    elif hasattr(value, "__dict__"):
        attrs = dir(value)
        info_parts.append("Attributes:")
        for attr in attrs:
            if not attr.startswith("_"):
                info_parts.append(f"- {attr}")

    # containers
    elif hasattr(value, "__len__"):
        info_parts.append(f"Length: {len(value)}")
        try:
            sample = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            info_parts.append(f"Sample: {sample}")
        except Exception:
            pass

    # any other object
    else:
        try:
            info_parts.append(f"Type: {type(value).__name__}")

            sample = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            info_parts.append(f"\nString representation: {sample}")

            if value.__doc__:
                doc = value.__doc__.strip()
                info_parts.append("Documentation:")
                info_parts.append(doc[:500] + "..." if len(doc) > 500 else doc)

        except Exception:
            pass

    return "\n".join(info_parts)


def get_context_for_variables(namespace: Dict[str, Any], query: str) -> str:
    """Extract relevant context from the user's namespace based on the query."""
    mentioned_vars = extract_variables_from_query(query)

    context_parts = []

    for var_name in mentioned_vars:
        if var_name in namespace:
            var = namespace[var_name]
            context_parts.append(get_variable_info(var_name, var))

    return "\n".join(context_parts)