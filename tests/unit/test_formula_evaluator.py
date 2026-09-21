import pytest
import logging
import math

from bcp.formula_evaluator import FormulaEvaluator
from bcp.logger import setup_logger


@pytest.fixture
def evaluator():
    logger = setup_logger(logging.DEBUG)
    return FormulaEvaluator(logger)


# --- sum() formulas ---

def test_sum_scores_extracted(evaluator):
    output = {"scores_extracted": [1, 3, 2, 8]}
    assert evaluator.evaluate("sum(scores_extracted)", output) == 14


def test_sum_empty_array(evaluator):
    output = {"scores_extracted": []}
    assert evaluator.evaluate("sum(scores_extracted)", output) == 0


def test_sum_single_element(evaluator):
    output = {"scores_extracted": [5]}
    assert evaluator.evaluate("sum(scores_extracted)", output) == 5


def test_sum_missing_field(evaluator):
    output = {}
    result = evaluator.evaluate("sum(scores_extracted)", output)
    assert result == 0


# --- count() formulas ---

def test_count_notification_events(evaluator):
    output = {"notification_events": ["event1", "event2", "event3"]}
    assert evaluator.evaluate("count(notification_events)", output) == 3


def test_count_empty_array(evaluator):
    output = {"notification_events": []}
    assert evaluator.evaluate("count(notification_events)", output) == 0


def test_count_audited_entities(evaluator):
    output = {"audited_entities": [{"entity": "User"}, {"entity": "Order"}]}
    assert evaluator.evaluate("count(audited_entities)", output) == 2


def test_count_missing_field(evaluator):
    output = {}
    result = evaluator.evaluate("count(notification_events)", output)
    assert result == 0


# --- direct dimension value formulas ---

def test_dimension_direct_value(evaluator):
    output = {"dimension_solution_variabilities": 3}
    assert evaluator.evaluate("dimension_solution_variabilities", output) == 3


def test_dimension_zero(evaluator):
    output = {"dimension_roles_permissions": 0}
    assert evaluator.evaluate("dimension_roles_permissions", output) == 0


def test_dimension_missing_returns_zero(evaluator):
    output = {}
    result = evaluator.evaluate("dimension_domain_entities", output)
    assert result == 0


# --- interface elements formula (complex with ceil) ---

def test_interface_elements_new_context(evaluator):
    """New context: static_weight=3, dynamic_weight=8"""
    output = {
        "static_elements": ["a", "b", "c", "d", "e"],  # 5 elements
        "dynamic_elements": ["x", "y", "z", "w", "v"],  # 5 elements
        "static_weight": 3,
        "dynamic_weight": 8,
    }
    # ceil(5/5)*3 + ceil(5/5)*8 = 1*3 + 1*8 = 11
    assert evaluator.evaluate(
        "ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight",
        output
    ) == 11


def test_interface_elements_existing_context(evaluator):
    """Existing context: static_weight=2, dynamic_weight=5"""
    output = {
        "static_elements": ["a", "b"],  # 2 elements
        "dynamic_elements": ["x"],  # 1 element
        "static_weight": 2,
        "dynamic_weight": 5,
    }
    # ceil(2/5)*2 + ceil(1/5)*5 = 1*2 + 1*5 = 7
    assert evaluator.evaluate(
        "ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight",
        output
    ) == 7


def test_interface_elements_empty(evaluator):
    output = {
        "static_elements": [],
        "dynamic_elements": [],
        "static_weight": 3,
        "dynamic_weight": 8,
    }
    # ceil(0/5)*3 + ceil(0/5)*8 = 0
    assert evaluator.evaluate(
        "ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight",
        output
    ) == 0


def test_interface_elements_large_count(evaluator):
    output = {
        "static_elements": ["a"] * 12,  # 12 elements → ceil(12/5) = 3
        "dynamic_elements": ["x"] * 7,  # 7 elements → ceil(7/5) = 2
        "static_weight": 3,
        "dynamic_weight": 8,
    }
    # 3*3 + 2*8 = 9 + 16 = 25
    assert evaluator.evaluate(
        "ceil(count(static_elements)/5)*static_weight + ceil(count(dynamic_elements)/5)*dynamic_weight",
        output
    ) == 25


# --- new domain entities formula ---

def test_new_domain_entities_block_a_only(evaluator):
    output = {
        "block_a_modified": ["e1", "e2", "e3"],  # ceil(3/3) = 1
        "block_b_new": [],  # ceil(0/3) = 0
    }
    # 2*1 + 5*0 = 2
    assert evaluator.evaluate(
        "2*ceil(count(block_a_modified)/3) + 5*ceil(count(block_b_new)/3)",
        output
    ) == 2


def test_new_domain_entities_both_blocks(evaluator):
    output = {
        "block_a_modified": ["e1", "e2", "e3", "e4", "e5"],  # ceil(5/3) = 2
        "block_b_new": ["e6", "e7", "e8"],  # ceil(3/3) = 1
    }
    # 2*2 + 5*1 = 9
    assert evaluator.evaluate(
        "2*ceil(count(block_a_modified)/3) + 5*ceil(count(block_b_new)/3)",
        output
    ) == 9


def test_new_domain_entities_empty(evaluator):
    output = {
        "block_a_modified": [],
        "block_b_new": [],
    }
    assert evaluator.evaluate(
        "2*ceil(count(block_a_modified)/3) + 5*ceil(count(block_b_new)/3)",
        output
    ) == 0


# --- aggregator formula (bindings) ---

def test_aggregator_sum_of_bindings(evaluator):
    bindings = {
        "dim_business_rules": 8,
        "dim_interface_elements": 11,
        "dim_solution_variabilities": 3,
        "dim_domain_entities": 2,
        "dim_new_domain_entities": 4,
        "dim_roles_permissions": 3,
        "dim_boundaries": 5,
        "dim_background_processes": 5,
        "dim_notifications": 2,
        "dim_audits": 1,
    }
    formula = "dim_business_rules + dim_interface_elements + dim_solution_variabilities + dim_domain_entities + dim_new_domain_entities + dim_roles_permissions + dim_boundaries + dim_background_processes + dim_notifications + dim_audits"
    assert evaluator.evaluate(formula, output={}, bindings=bindings) == 44


def test_aggregator_with_zero_bindings(evaluator):
    bindings = {f"dim_{d}": 0 for d in [
        "business_rules", "interface_elements", "solution_variabilities",
        "domain_entities", "new_domain_entities", "roles_permissions",
        "boundaries", "background_processes", "notifications", "audits"
    ]}
    formula = "dim_business_rules + dim_interface_elements + dim_solution_variabilities + dim_domain_entities + dim_new_domain_entities + dim_roles_permissions + dim_boundaries + dim_background_processes + dim_notifications + dim_audits"
    assert evaluator.evaluate(formula, output={}, bindings=bindings) == 0


# --- NFR formula ---

def test_nfr_sum(evaluator):
    output = {
        "dimension_quality_attributes": 3,
        "dimension_security_compliance": 5,
        "dimension_user_experience_accessibility": 1,
    }
    formula = "dimension_quality_attributes + dimension_security_compliance + dimension_user_experience_accessibility"
    assert evaluator.evaluate(formula, output) == 9


def test_nfr_all_zero(evaluator):
    output = {
        "dimension_quality_attributes": 0,
        "dimension_security_compliance": 0,
        "dimension_user_experience_accessibility": 0,
    }
    formula = "dimension_quality_attributes + dimension_security_compliance + dimension_user_experience_accessibility"
    assert evaluator.evaluate(formula, output) == 0


# --- edge cases ---

def test_empty_formula_raises(evaluator):
    with pytest.raises(ValueError):
        evaluator.evaluate("", {})


def test_invalid_formula_raises(evaluator):
    with pytest.raises(ValueError):
        evaluator.evaluate("invalid_func(123)", {"invalid_func": 1})


def test_formula_with_none_value(evaluator):
    output = {"dimension_solution_variabilities": None}
    # None is not int/float, so it's treated as missing → defaults to 0
    result = evaluator.evaluate("dimension_solution_variabilities", output)
    assert result == 0
