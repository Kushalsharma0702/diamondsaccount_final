"""
T1 Validation Engine
====================
Reads T1Structure.json and enforces all validation rules for T1 Personal Tax Forms.

This service validates:
- Field types (text, number, boolean, date, email, phone)
- Required fields
- MaxLength constraints
- Select field options
- Conditional visibility (shownWhen)
- Repeatable subforms

Single source of truth: backend/T1Structure (2).json
"""

import json
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path


class T1ValidationEngine:
    """
    T1 Personal Tax Form validation engine.
    Loads T1Structure.json at startup and validates draft/submission data.
    """
    
    def __init__(self, structure_path: Optional[str] = None):
        """
        Initialize the validation engine with T1Structure.json
        
        Args:
            structure_path: Path to T1Structure.json (defaults to backend/T1Structure (2).json)
        """
        if structure_path is None:
            # Default path: backend/T1Structure (2).json
            base_dir = Path(__file__).parent.parent.parent
            structure_path = base_dir / "T1Structure (2).json"
        
        self.structure_path = structure_path
        self.structure = self._load_structure()
        self.field_registry = self._build_field_registry()
        self.condition_registry = self._build_condition_registry()
    
    def _load_structure(self) -> Dict[str, Any]:
        """Load and parse T1Structure.json"""
        try:
            with open(self.structure_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"T1Structure.json not found at {self.structure_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in T1Structure.json: {e}")
    
    def _build_field_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a flat registry of all fields from T1Structure.json
        Returns: {field_key: field_definition}
        """
        registry = {}
        
        for step in self.structure.get("steps", []):
            if step.get("id") == "personal_info":
                # Process personal info sections
                for section in step.get("sections", []):
                    for field in section.get("fields", []):
                        registry[field["key"]] = {
                            **field,
                            "step_id": step["id"],
                            "section_id": section["id"],
                            "section_condition": section.get("shownWhen")
                        }
            
            elif step.get("id") == "questionnaire":
                # Process questionnaire questions
                for question in step.get("questions", []):
                    registry[question["key"]] = {
                        **question,
                        "step_id": step["id"],
                        "is_question": True
                    }
                    
                    # Process subform fields if present
                    subform = question.get("subform", {})
                    if subform and "fields" in subform:
                        for field in subform["fields"]:
                            if isinstance(field, dict) and "label" in field:
                                # Generate a pseudo-key for subform fields
                                field_key = f"{question['key']}.{field['label'].replace(' ', '_').lower()}"
                                registry[field_key] = {
                                    **field,
                                    "step_id": step["id"],
                                    "parent_question": question["key"],
                                    "condition": subform.get("shownWhen")
                                }
            
            elif step.get("id") == "detail_steps":
                # Process detail steps (movingExpenses, uberSkipDoordash, etc.)
                for detail_step in step.get("steps", []):
                    trigger = detail_step.get("trigger", {})
                    for subform in detail_step.get("subforms", []):
                        for field in subform.get("fields", []):
                            if isinstance(field, dict) and "key" in field:
                                registry[field["key"]] = {
                                    **field,
                                    "step_id": detail_step["id"],
                                    "trigger": trigger,
                                    "subform_condition": subform.get("shownWhen")
                                }
                    
                    # Process fields directly under detail step
                    for field in detail_step.get("fields", []):
                        if isinstance(field, dict) and "key" in field:
                            registry[field["key"]] = {
                                **field,
                                "step_id": detail_step["id"],
                                "trigger": trigger
                            }
        
        return registry
    
    def _build_condition_registry(self) -> Dict[str, List[str]]:
        """
        Build a registry mapping field keys to dependent field keys
        Returns: {field_key: [dependent_field_keys]}
        """
        registry = {}
        
        for field_key, field_def in self.field_registry.items():
            # Check section-level conditions
            section_condition = field_def.get("section_condition")
            if section_condition:
                watched_key = section_condition.get("key")
                if watched_key:
                    if watched_key not in registry:
                        registry[watched_key] = []
                    registry[watched_key].append(field_key)
            
            # Check field-level conditions
            condition = field_def.get("condition") or field_def.get("trigger")
            if condition and isinstance(condition, dict):
                watched_key = condition.get("key")
                if watched_key:
                    if watched_key not in registry:
                        registry[watched_key] = []
                    registry[watched_key].append(field_key)
        
        return registry
    
    def validate_draft_save(self, answers: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate draft save (partial validation).
        Only validates fields that are present in answers.
        
        Args:
            answers: {field_key: value} dictionary
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        for field_key, value in answers.items():
            # Skip None/empty values in draft mode
            if value is None or value == "":
                continue
            
            # Get field definition
            field_def = self.field_registry.get(field_key)
            if not field_def:
                # In draft mode, allow unknown fields (store as JSONB)
                # They may be custom fields from mobile app
                # Only validate type for basic safety
                continue
            
            # Validate type
            type_valid, type_error = self._validate_type(field_key, value, field_def)
            if not type_valid:
                errors.append(type_error)
            
            # Validate maxLength
            if "maxLength" in field_def and isinstance(value, str):
                if len(value) > field_def["maxLength"]:
                    errors.append(f"{field_key}: Exceeds max length of {field_def['maxLength']}")
            
            # Validate select options
            if field_def.get("type") == "select" and "options" in field_def:
                if value not in field_def["options"]:
                    errors.append(f"{field_key}: Invalid option '{value}'. Must be one of {field_def['options']}")
        
        return len(errors) == 0, errors
    
    def validate_submission(self, answers: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate T1 submission (complete validation).
        Enforces all required fields based on conditional logic.
        
        Args:
            answers: {field_key: value} dictionary
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # First validate types and constraints for present fields
        draft_valid, draft_errors = self.validate_draft_save(answers)
        if not draft_valid:
            errors.extend(draft_errors)
        
        # Check required fields (considering conditional visibility)
        required_fields = self._get_required_fields(answers)
        for field_key in required_fields:
            if field_key not in answers or answers[field_key] is None or answers[field_key] == "":
                field_def = self.field_registry.get(field_key, {})
                label = field_def.get("label", field_key)
                errors.append(f"Required field missing: {label} ({field_key})")
        
        return len(errors) == 0, errors
    
    def _get_required_fields(self, answers: Dict[str, Any]) -> Set[str]:
        """
        Determine which fields are required based on current answers and conditional logic.
        
        Args:
            answers: Current form answers
            
        Returns:
            Set of required field keys
        """
        required = set()
        
        for field_key, field_def in self.field_registry.items():
            # Check if field is required
            if not field_def.get("required", False):
                continue
            
            # Check if field is conditionally visible
            if not self._is_field_visible(field_key, field_def, answers):
                continue
            
            required.add(field_key)
        
        return required
    
    def _is_field_visible(self, field_key: str, field_def: Dict[str, Any], answers: Dict[str, Any]) -> bool:
        """
        Check if a field is visible based on conditional logic (shownWhen).
        
        Args:
            field_key: The field key
            field_def: Field definition from registry
            answers: Current form answers
            
        Returns:
            True if field should be visible
        """
        # Check section-level condition
        section_condition = field_def.get("section_condition")
        if section_condition:
            if not self._evaluate_condition(section_condition, answers):
                return False
        
        # Check field-level condition
        condition = field_def.get("condition")
        if condition:
            if not self._evaluate_condition(condition, answers):
                return False
        
        # Check trigger condition (for detail steps)
        trigger = field_def.get("trigger")
        if trigger:
            if not self._evaluate_condition(trigger, answers):
                return False
        
        # Check subform condition
        subform_condition = field_def.get("subform_condition")
        if subform_condition:
            if not self._evaluate_condition(subform_condition, answers):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], answers: Dict[str, Any]) -> bool:
        """
        Evaluate a shownWhen/trigger condition.
        
        Args:
            condition: {key: "...", operator: "equals"|"in"|"contains", value: ...}
            answers: Current form answers
            
        Returns:
            True if condition is met
        """
        watched_key = condition.get("key")
        operator = condition.get("operator", "equals")
        expected_value = condition.get("value")
        
        if not watched_key:
            return True  # No condition, always visible
        
        actual_value = answers.get(watched_key)
        
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "in":
            if isinstance(expected_value, list):
                return actual_value in expected_value
            return False
        elif operator == "contains":
            if isinstance(actual_value, list):
                return expected_value in actual_value
            if isinstance(actual_value, str):
                return expected_value in actual_value
            return False
        else:
            # Unknown operator, fail-closed
            return False
    
    def _validate_type(self, field_key: str, value: Any, field_def: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate field type.
        
        Args:
            field_key: Field key
            value: Field value
            field_def: Field definition
            
        Returns:
            (is_valid, error_message)
        """
        field_type = field_def.get("type")
        label = field_def.get("label", field_key)
        
        if field_type == "text":
            if not isinstance(value, str):
                return False, f"{label}: Must be text"
        
        elif field_type == "number":
            try:
                # Accept int, float, or numeric string
                if isinstance(value, str):
                    Decimal(value)
                elif not isinstance(value, (int, float, Decimal)):
                    return False, f"{label}: Must be a number"
            except (InvalidOperation, ValueError):
                return False, f"{label}: Invalid number format"
        
        elif field_type == "boolean":
            if not isinstance(value, bool):
                return False, f"{label}: Must be true or false"
        
        elif field_type == "date":
            if isinstance(value, str):
                # Validate ISO date format (YYYY-MM-DD)
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    return False, f"{label}: Invalid date format (expected YYYY-MM-DD)"
            elif not isinstance(value, datetime):
                return False, f"{label}: Must be a date"
        
        elif field_type == "email":
            if not isinstance(value, str):
                return False, f"{label}: Must be text"
            # Basic email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                return False, f"{label}: Invalid email format"
        
        elif field_type == "phone":
            if not isinstance(value, str):
                return False, f"{label}: Must be text"
            # Canadian phone number validation (10 digits)
            phone_pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
            if not re.match(phone_pattern, value.replace(" ", "")):
                return False, f"{label}: Invalid phone format (expected 10 digits)"
        
        elif field_type == "select":
            if not isinstance(value, str):
                return False, f"{label}: Must be text"
        
        return True, ""
    
    def get_required_documents(self, answers: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Compute required documents based on questionnaire answers.
        
        Args:
            answers: Current form answers
            
        Returns:
            List of {label, question_key, shownWhen}
        """
        required_docs = []
        
        # Get document requirements from structure
        doc_requirements = self.structure.get("documentRequirements", [])
        
        for doc_req in doc_requirements:
            label = doc_req.get("label")
            shown_when = doc_req.get("shownWhen")
            
            if not shown_when:
                # Always required
                required_docs.append({
                    "label": label,
                    "question_key": None,
                    "shownWhen": None
                })
            elif self._evaluate_condition(shown_when, answers):
                # Conditionally required
                required_docs.append({
                    "label": label,
                    "question_key": shown_when.get("key"),
                    "shownWhen": shown_when
                })
        
        # Also check questions with documentsRequired
        for step in self.structure.get("steps", []):
            if step.get("id") == "questionnaire":
                for question in step.get("questions", []):
                    question_key = question.get("key")
                    docs_required = question.get("documentsRequired", [])
                    
                    # Check if question is answered "yes"
                    if answers.get(question_key) == True:
                        for doc_label in docs_required:
                            required_docs.append({
                                "label": doc_label,
                                "question_key": question_key,
                                "shownWhen": {"key": question_key, "operator": "equals", "value": True}
                            })
        
        return required_docs
    
    def get_structure_json(self) -> Dict[str, Any]:
        """Return the raw T1Structure.json for frontend consumption"""
        return self.structure
    
    def calculate_completion_percentage(self, answers: Dict[str, Any]) -> int:
        """
        Calculate form completion percentage based on required fields.
        
        Args:
            answers: Current form answers
            
        Returns:
            Completion percentage (0-100)
        """
        required_fields = self._get_required_fields(answers)
        if not required_fields:
            return 0
        
        completed_fields = sum(
            1 for field_key in required_fields
            if field_key in answers and answers[field_key] not in [None, ""]
        )
        
        return int((completed_fields / len(required_fields)) * 100)


# Global instance (initialized at application startup)
_validation_engine: Optional[T1ValidationEngine] = None


def get_validation_engine() -> T1ValidationEngine:
    """Get the global T1ValidationEngine instance"""
    global _validation_engine
    if _validation_engine is None:
        _validation_engine = T1ValidationEngine()
    return _validation_engine


def initialize_validation_engine(structure_path: Optional[str] = None):
    """Initialize the validation engine at application startup"""
    global _validation_engine
    _validation_engine = T1ValidationEngine(structure_path)
