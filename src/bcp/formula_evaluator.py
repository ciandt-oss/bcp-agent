"""
Formula Evaluator for BCP 13-Dimensions Pipeline

Evaluates scoreFormula strings from pipeline cell definitions against the JSON
output produced by each LLM cell. Supports the formula types used in
ThirteenPipeline V2:

- sum(field)              → sum of an integer array field
- count(field)            → length of an array field
- dimension_<name>        → direct numeric field value
- ceil(count(a)/N)*w ...  → arithmetic with ceil, count, multiplication, addition
- dim_<name> + dim_<name> → sum of binding values (aggregator)

The evaluator uses a safe AST-based approach — never eval().
"""

import ast
import logging
import math
import re
from typing import Dict, Any, Optional


class FormulaEvaluator:
    """
    Safely evaluates scoreFormula expressions against cell output and bindings.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def evaluate(
        self,
        formula: str,
        output: Dict[str, Any],
        bindings: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Evaluate a scoreFormula and return the numeric score.

        Args:
            formula: The formula string (e.g. "sum(scores_extracted)")
            output: The parsed JSON output dict from the LLM cell
            bindings: Optional dict of binding values from upstream cells

        Returns:
            The evaluated score as a number (int or float)

        Raises:
            ValueError: If the formula cannot be evaluated
        """
        if not formula or not formula.strip():
            raise ValueError("Empty formula")

        bindings = bindings or {}

        try:
            transformed = self._transform_formula(formula, output, bindings)
            result = self._safe_eval(transformed)
            score = int(result) if isinstance(result, float) and result.is_integer() else result
            self.logger.debug(
                f"Formula '{formula}' → '{transformed}' → {score}"
            )
            return score
        except Exception as e:
            self.logger.error(
                f"Failed to evaluate formula '{formula}': {str(e)}. "
                f"Output keys: {list(output.keys())}, Bindings: {list(bindings.keys())}"
            )
            raise ValueError(f"Formula evaluation failed: {formula}") from e

    def _transform_formula(
        self,
        formula: str,
        output: Dict[str, Any],
        bindings: Dict[str, Any],
    ) -> str:
        """
        Transform a formula string into a pure arithmetic Python expression
        by replacing function calls and field references with concrete values.
        """
        result = formula

        # Replace count(field) → len of the array (as number)
        result = self._replace_count(result, output)

        # Replace sum(field) → sum of the array (as number)
        result = self._replace_sum(result, output)

        # Replace ceil(...) → math.ceil(...)  — keep as Python expression
        result = result.replace("ceil(", "_ceil(")

        # Replace dimension_* field references with values from output
        result = self._replace_field_refs(result, output, bindings)

        return result

    @staticmethod
    def _replace_count(formula: str, output: Dict[str, Any]) -> str:
        """Replace count(field_name) with the length of the array at output[field_name]."""
        def replacer(match):
            field = match.group(1).strip()
            arr = output.get(field, [])
            if isinstance(arr, list):
                return str(len(arr))
            if arr is None:
                return "0"
            return str(arr)

        return re.sub(r"count\(([^()]+)\)", replacer, formula)

    @staticmethod
    def _replace_sum(formula: str, output: Dict[str, Any]) -> str:
        """Replace sum(field_name) with the sum of the array at output[field_name]."""
        def replacer(match):
            field = match.group(1).strip()
            arr = output.get(field, [])
            if isinstance(arr, list):
                vals = [v for v in arr if isinstance(v, (int, float))]
                return str(sum(vals))
            if isinstance(arr, (int, float)):
                return str(arr)
            return "0"

        return re.sub(r"sum\(([^()]+)\)", replacer, formula)

    @staticmethod
    def _replace_field_refs(
        formula: str,
        output: Dict[str, Any],
        bindings: Dict[str, Any],
    ) -> str:
        """
        Replace bare identifiers (dimension_*, dim_*, static_weight, dynamic_weight)
        with their numeric values from output or bindings.
        """
        # Collect all identifiers that look like field/binding references
        # Pattern: word characters and dots, not preceded by '(' and not followed by '('
        identifiers = set(re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", formula))

        # Remove function names that should not be replaced
        builtins = {"_ceil", "ceil", "count", "sum", "len", "math"}

        result = formula
        for ident in identifiers:
            if ident in builtins:
                continue

            value = None
            if ident in bindings:
                value = bindings[ident]
            elif ident in output:
                value = output[ident]

            if value is not None and isinstance(value, (int, float)):
                result = re.sub(rf"\b{re.escape(ident)}\b", str(value), result)
            else:
                # Identifier not found in output or bindings — default to 0
                result = re.sub(rf"\b{re.escape(ident)}\b", "0", result)

        return result

    @staticmethod
    def _safe_eval(expr: str) -> Any:
        """
        Safely evaluate a transformed arithmetic expression.

        Uses ast.parse with mode='eval' and a restricted node visitor.
        Only allows: numbers, +, -, *, /, //, %, **, parentheses, and _ceil calls.
        """
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid expression: {expr}") from e

        return _SafeEvalVisitor().visit(tree.body)


class _SafeEvalVisitor(ast.NodeVisitor):
    """
    AST visitor that evaluates a restricted set of Python expressions.
    Supports: constants (numbers), arithmetic ops, and _ceil function calls.
    """

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value}")

    def visit_Num(self, node: ast.Num) -> Any:  # noqa: F811 — deprecated but kept for older Python
        return node.n

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name) and node.func.id == "_ceil":
            if len(node.args) != 1:
                raise ValueError("_ceil expects exactly 1 argument")
            arg = self.visit(node.args[0])
            return math.ceil(arg)
        raise ValueError(f"Unsupported function call: {ast.dump(node.func)}")

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")
