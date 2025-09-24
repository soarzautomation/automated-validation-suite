#!/usr/bin/env python3
"""
Automated Validation Suite - Core Validation Engine
Systematically validates simulation input files against configurable rule sets

Based on real-world simulation validation experience.
Author: Ryan Hendrix - SOARZ Automation
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationRule:
    """
    Base class for validation rules
    """
    def __init__(self, rule_id, description, severity='ERROR'):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity  # ERROR, WARNING, INFO
    
    def validate(self, file_data, context=None):
        """
        Override this method in specific rule implementations
        Returns ValidationResult object
        """
        raise NotImplementedError("Subclasses must implement validate method")

class ValidationResult:
    """
    Result of a single validation rule check
    """
    def __init__(self, rule_id, passed, message, severity='ERROR', details=None):
        self.rule_id = rule_id
        self.passed = passed
        self.message = message
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()

class ValidationReport:
    """
    Comprehensive validation report containing all rule results
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.results = []
        self.summary = {
            'total_rules': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'errors': 0
        }
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_result(self, result):
        """Add a validation result to the report"""
        self.results.append(result)
        self.summary['total_rules'] += 1
        
        if result.passed:
            self.summary['passed'] += 1
        else:
            self.summary['failed'] += 1
            if result.severity == 'ERROR':
                self.summary['errors'] += 1
            elif result.severity == 'WARNING':
                self.summary['warnings'] += 1
    
    def finalize(self):
        """Mark report as complete"""
        self.end_time = datetime.now()
        self.summary['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
    
    def is_valid(self):
        """Return True if no critical errors found"""
        return self.summary['errors'] == 0
    
    def get_critical_errors(self):
        """Get all critical error results"""
        return [r for r in self.results if not r.passed and r.severity == 'ERROR']
    
    def get_warnings(self):
        """Get all warning results"""
        return [r for r in self.results if not r.passed and r.severity == 'WARNING']

class ValidationEngine:
    """
    Main validation engine that orchestrates rule execution
    """
    
    def __init__(self, config_path=None):
        self.rules = []
        self.config = self._load_config(config_path)
        self._initialize_rules()
    
    def _load_config(self, config_path):
        """Load validation configuration"""
        default_config = {
            'file_types': ['.dat', '.inp', '.txt', '.csv', '.json'],
            'parameter_ranges': {
                'temperature': (200, 800),
                'pressure': (0, 500000),
                'velocity': (0, 100),
                'density': (0.1, 10000)
            },
            'required_files': ['input.dat', 'boundary_conditions.txt', 'material_properties.csv'],
            'validation_rules': [
                'file_existence',
                'file_format',
                'parameter_ranges',
                'cross_file_consistency',
                'physics_validation'
            ]
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _initialize_rules(self):
        """Initialize validation rules based on configuration"""
        rule_classes = {
            'file_existence': FileExistenceRule,
            'file_format': FileFormatRule,
            'parameter_ranges': ParameterRangeRule,
            'cross_file_consistency': CrossFileConsistencyRule,
            'physics_validation': PhysicsValidationRule
        }
        
        for rule_name in self.config['validation_rules']:
            if rule_name in rule_classes:
                rule_class = rule_classes[rule_name]
                rule_instance = rule_class(self.config)
                self.rules.append(rule_instance)
    
    def validate_model(self, model_path):
        """
        Run complete validation suite against simulation model
        """
        model_path = Path(model_path)
        model_name = model_path.name
        
        logger.info(f"Starting validation of model: {model_name}")
        
        # Create validation report
        report = ValidationReport(model_name)
        
        # Load model data
        model_data = self._load_model_data(model_path)
        
        # Execute all validation rules
        for rule in self.rules:
            try:
                result = rule.validate(model_data, context={'model_path': model_path})
                report.add_result(result)
                
                status = "PASS" if result.passed else f"FAIL ({result.severity})"
                logger.info(f"Rule {rule.rule_id}: {status} - {result.message}")
                
            except Exception as e:
                error_result = ValidationResult(
                    rule.rule_id,
                    False,
                    f"Rule execution failed: {str(e)}",
                    'ERROR',
                    {'exception': str(e)}
                )
                report.add_result(error_result)
                logger.error(f"Rule {rule.rule_id} failed with exception: {e}")
        
        report.finalize()
        logger.info(f"Validation complete. Status: {'VALID' if report.is_valid() else 'INVALID'}")
        
        return report
    
    def _load_model_data(self, model_path):
        """Load all model files and extract data"""
        model_data = {
            'files': {},
            'parameters': {},
            'metadata': {
                'model_path': model_path,
                'file_count': 0,
                'total_size': 0
            }
        }
        
        # Scan for all relevant files
        for file_path in model_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.config['file_types']:
                relative_path = file_path.relative_to(model_path)
                
                try:
                    # Read file content
                    content = self._read_file_safely(file_path)
                    model_data['files'][str(relative_path)] = {
                        'path': file_path,
                        'content': content,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    }
                    
                    # Extract parameters if possible
                    parameters = self._extract_parameters(content)
                    if parameters:
                        model_data['parameters'].update(parameters)
                    
                    model_data['metadata']['file_count'] += 1
                    model_data['metadata']['total_size'] += file_path.stat().st_size
                    
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")
        
        return model_data
    
    def _read_file_safely(self, file_path):
        """Safely read file content with encoding detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return "[BINARY_FILE]"
    
    def _extract_parameters(self, content):
        """Extract parameter values from file content"""
        parameters = {}
        
        # Look for common parameter patterns
        patterns = [
            r'(\w+)\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',  # key=value
            r'(\w+):\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',     # key: value
            r'(\w+)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'      # key value
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for key, value in matches:
                try:
                    parameters[key.lower()] = float(value)
                except ValueError:
                    continue
        
        return parameters

# Specific validation rule implementations

class FileExistenceRule(ValidationRule):
    """Check that all required files exist"""
    
    def __init__(self, config):
        super().__init__(
            'FILE_EXISTENCE',
            'Verify all required files are present',
            'ERROR'
        )
        self.required_files = config.get('required_files', [])
    
    def validate(self, model_data, context=None):
        missing_files = []
        present_files = list(model_data['files'].keys())
        
        for required_file in self.required_files:
            # Check for exact match or pattern match
            found = any(required_file.lower() in f.lower() for f in present_files)
            if not found:
                missing_files.append(required_file)
        
        if missing_files:
            return ValidationResult(
                self.rule_id,
                False,
                f"Missing required files: {', '.join(missing_files)}",
                self.severity,
                {'missing_files': missing_files, 'present_files': present_files}
            )
        else:
            return ValidationResult(
                self.rule_id,
                True,
                f"All {len(self.required_files)} required files present",
                'INFO'
            )

class FileFormatRule(ValidationRule):
    """Validate file formats and basic structure"""
    
    def __init__(self, config):
        super().__init__(
            'FILE_FORMAT',
            'Verify file formats and basic structure',
            'ERROR'
        )
        self.config = config
    
    def validate(self, model_data, context=None):
        format_errors = []
        
        for filename, file_info in model_data['files'].items():
            content = file_info['content']
            
            # Check for empty files
            if not content or content == "[BINARY_FILE]":
                format_errors.append(f"{filename}: Empty or unreadable file")
                continue
            
            # Check for basic structure based on file type
            if filename.endswith('.csv'):
                if ',' not in content:
                    format_errors.append(f"{filename}: CSV file missing comma separators")
            
            elif filename.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    format_errors.append(f"{filename}: Invalid JSON format - {str(e)}")
            
            elif filename.endswith(('.dat', '.inp')):
                # Check for reasonable line count and structure
                lines = content.split('\n')
                if len(lines) < 2:
                    format_errors.append(f"{filename}: File appears incomplete (only {len(lines)} lines)")
        
        if format_errors:
            return ValidationResult(
                self.rule_id,
                False,
                f"Format issues found in {len(format_errors)} files",
                self.severity,
                {'format_errors': format_errors}
            )
        else:
            return ValidationResult(
                self.rule_id,
                True,
                f"All {len(model_data['files'])} files have valid formats",
                'INFO'
            )

class ParameterRangeRule(ValidationRule):
    """Validate parameter values are within acceptable ranges"""
    
    def __init__(self, config):
        super().__init__(
            'PARAMETER_RANGES',
            'Verify parameters are within acceptable ranges',
            'ERROR'
        )
        self.parameter_ranges = config.get('parameter_ranges', {})
    
    def validate(self, model_data, context=None):
        range_violations = []
        parameters = model_data.get('parameters', {})
        
        for param_name, param_value in parameters.items():
            if param_name in self.parameter_ranges:
                min_val, max_val = self.parameter_ranges[param_name]
                
                if param_value < min_val or param_value > max_val:
                    range_violations.append({
                        'parameter': param_name,
                        'value': param_value,
                        'range': f"{min_val} to {max_val}",
                        'violation_type': 'below_minimum' if param_value < min_val else 'above_maximum'
                    })
        
        if range_violations:
            violation_msgs = []
            for v in range_violations:
                violation_msgs.append(f"{v['parameter']}={v['value']} (valid range: {v['range']})")
            
            return ValidationResult(
                self.rule_id,
                False,
                f"Parameter range violations: {'; '.join(violation_msgs)}",
                self.severity,
                {'violations': range_violations}
            )
        else:
            checked_params = len([p for p in parameters.keys() if p in self.parameter_ranges])
            return ValidationResult(
                self.rule_id,
                True,
                f"All {checked_params} checked parameters within valid ranges",
                'INFO'
            )

class CrossFileConsistencyRule(ValidationRule):
    """Check consistency between related files"""
    
    def __init__(self, config):
        super().__init__(
            'CROSS_FILE_CONSISTENCY',
            'Verify consistency between related files',
            'WARNING'
        )
        self.config = config
    
    def validate(self, model_data, context=None):
        consistency_issues = []
        parameters = model_data.get('parameters', {})
        
        # Example consistency checks
        # Check if temperature is consistent across files
        temperature_values = [(k, v) for k, v in parameters.items() if 'temp' in k.lower()]
        if len(temperature_values) > 1:
            temps = [v for k, v in temperature_values]
            if max(temps) - min(temps) > 50:  # More than 50 degree difference
                consistency_issues.append(
                    f"Temperature values vary significantly: {dict(temperature_values)}"
                )
        
        # Check file count consistency
        file_count = model_data['metadata']['file_count']
        if file_count < 3:
            consistency_issues.append(
                f"Only {file_count} input files found - typical models have 3+ files"
            )
        
        if consistency_issues:
            return ValidationResult(
                self.rule_id,
                False,
                f"Consistency issues found: {'; '.join(consistency_issues)}",
                self.severity,
                {'issues': consistency_issues}
            )
        else:
            return ValidationResult(
                self.rule_id,
                True,
                "Cross-file consistency checks passed",
                'INFO'
            )

class PhysicsValidationRule(ValidationRule):
    """Validate physics-based constraints"""
    
    def __init__(self, config):
        super().__init__(
            'PHYSICS_VALIDATION',
            'Verify physically realistic parameter combinations',
            'ERROR'
        )
        self.config = config
    
    def validate(self, model_data, context=None):
        physics_violations = []
        parameters = model_data.get('parameters', {})
        
        # Example physics checks
        temp = parameters.get('temperature', 0)
        pressure = parameters.get('pressure', 0)
        density = parameters.get('density', 0)
        
        # Check for physically impossible combinations
        if temp > 0 and pressure > 0:
            # Basic ideal gas law check (simplified)
            if density > 0:
                expected_density_ratio = pressure / temp
                actual_density_ratio = density / 100  # Normalize for comparison
                
                if abs(expected_density_ratio - actual_density_ratio) > expected_density_ratio * 0.5:
                    physics_violations.append(
                        f"Density ({density}) inconsistent with temperature ({temp}) and pressure ({pressure})"
                    )
        
        # Check for extreme values that might indicate unit errors
        if temp > 0 and temp < 10:  # Might be in wrong units (Celsius vs Kelvin)
            physics_violations.append(
                f"Temperature ({temp}) unusually low - check units (Kelvin vs Celsius)"
            )
        
        if physics_violations:
            return ValidationResult(
                self.rule_id,
                False,
                f"Physics violations detected: {'; '.join(physics_violations)}",
                self.severity,
                {'violations': physics_violations}
            )
        else:
            return ValidationResult(
                self.rule_id,
                True,
                "Physics validation checks passed",
                'INFO'
            )

def main():
    """
    Command-line interface for validation engine
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate simulation model input files')
    parser.add_argument('model_path', help='Path to simulation model directory')
    parser.add_argument('--config', '-c', help='Path to validation configuration file')
    parser.add_argument('--output', '-o', help='Output file for validation report (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input path
    if not os.path.exists(args.model_path):
        logger.error(f"Model path does not exist: {args.model_path}")
        return 1
    
    # Create validation engine
    engine = ValidationEngine(args.config)
    
    # Run validation
    report = engine.validate_model(args.model_path)
    
    # Output results
    if args.output:
        # Save detailed JSON report
        report_data = {
            'model_name': report.model_name,
            'summary': report.summary,
            'start_time': report.start_time.isoformat(),
            'end_time': report.end_time.isoformat() if report.end_time else None,
            'is_valid': report.is_valid(),
            'results': [
                {
                    'rule_id': r.rule_id,
                    'passed': r.passed,
                    'message': r.message,
                    'severity': r.severity,
                    'details': r.details,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in report.results
            ]
        }
        
        with open(args.output, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Detailed report saved to: {args.output}")
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Model: {report.model_name}")
    print(f"Status: {'VALID' if report.is_valid() else 'INVALID'}")
    print(f"Duration: {report.summary['duration_seconds']:.1f} seconds")
    print(f"Rules Executed: {report.summary['total_rules']}")
    print(f"Passed: {report.summary['passed']}")
    print(f"Failed: {report.summary['failed']}")
    print(f"Errors: {report.summary['errors']}")
    print(f"Warnings: {report.summary['warnings']}")
    
    # Show critical errors
    critical_errors = report.get_critical_errors()
    if critical_errors:
        print(f"\nCRITICAL ERRORS ({len(critical_errors)}):")
        for error in critical_errors:
            print(f"  [{error.rule_id}] {error.message}")
    
    # Show warnings
    warnings = report.get_warnings()
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  [{warning.rule_id}] {warning.message}")
    
    return 0 if report.is_valid() else 1

if __name__ == "__main__":
    exit(main())