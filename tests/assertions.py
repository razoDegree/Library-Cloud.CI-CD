# assertions.py
import sys

def assert_status_code(response, status_code):
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"

def assert_response_content(response, expected_content):
    assert response.json() == expected_content, f"Expected content {expected_content}, got {response.json()}"

def assert_valid_added_resource(response):
    assert response.status_code == 201, "Failed to create resource, status code not 201"
    assert response.json().get('ID'), "No valid ID returned"

def assert_field(response, field_name, expected_value):
    assert response.json().get(field_name) == expected_value, f"Field {field_name} expected value {expected_value}, got {response.json().get(field_name)}"