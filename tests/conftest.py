"""
Shared pytest configuration for the composite test suites.
"""

pytest_plugins = ["pytester", "tests._harness.network_guard"]
