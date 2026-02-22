"""Tests for WAF rules."""

import pytest
from app.security.waf_rules import WAFRules


class TestSQLInjection:
    """Test SQL injection detection."""

    def test_union_select_injection(self):
        """Test UNION SELECT injection detection."""
        payload = "1' UNION SELECT * FROM users--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_select_from_injection(self):
        """Test SELECT FROM injection detection."""
        payload = "'; SELECT * FROM users WHERE '1'='1"
        assert WAFRules.check_sql_injection(payload) is True

    def test_insert_into_injection(self):
        """Test INSERT INTO injection detection."""
        payload = "'; INSERT INTO users VALUES ('admin', 'password')--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_update_set_injection(self):
        """Test UPDATE SET injection detection."""
        payload = "'; UPDATE users SET password='hacked'--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_delete_from_injection(self):
        """Test DELETE FROM injection detection."""
        payload = "'; DELETE FROM users--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_drop_table_injection(self):
        """Test DROP TABLE injection detection."""
        payload = "'; DROP TABLE users--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_sql_comment_injection(self):
        """Test SQL comment injection detection."""
        payload = "admin'--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_or_injection(self):
        """Test OR injection detection."""
        payload = "' OR '1'='1"
        assert WAFRules.check_sql_injection(payload) is True

    def test_and_injection(self):
        """Test AND injection detection."""
        payload = "' AND 1=1--"
        assert WAFRules.check_sql_injection(payload) is True

    def test_legitimate_text(self):
        """Test legitimate text is not flagged."""
        payload = "John Doe"
        assert WAFRules.check_sql_injection(payload) is False

    def test_legitimate_email(self):
        """Test legitimate email is not flagged."""
        payload = "user@example.com"
        assert WAFRules.check_sql_injection(payload) is False


class TestNoSQLInjection:
    """Test NoSQL injection detection."""

    def test_where_operator(self):
        """Test $where operator detection."""
        payload = {"$where": "this.password == 'admin'"}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_regex_operator(self):
        """Test $regex operator detection."""
        payload = {"username": {"$regex": "^admin"}}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_ne_operator(self):
        """Test $ne operator detection."""
        payload = {"password": {"$ne": ""}}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_gt_operator(self):
        """Test $gt operator detection."""
        payload = {"age": {"$gt": 0}}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_or_operator(self):
        """Test $or operator detection."""
        payload = {"$or": [{"username": "admin"}, {"password": "admin"}]}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_legitimate_dict(self):
        """Test legitimate dictionary is not flagged."""
        payload = {"username": "john", "email": "john@example.com"}
        assert WAFRules.check_nosql_injection(payload) is False

    def test_nested_injection(self):
        """Test nested NoSQL injection detection."""
        payload = {"user": {"$ne": None}}
        assert WAFRules.check_nosql_injection(payload) is True

    def test_list_injection(self):
        """Test NoSQL injection in list."""
        payload = [{"$or": [{"a": 1}]}]
        assert WAFRules.check_nosql_injection(payload) is True


class TestXSSDetection:
    """Test XSS detection."""

    def test_script_tag(self):
        """Test script tag detection."""
        payload = "<script>alert('XSS')</script>"
        assert WAFRules.check_xss(payload) is True

    def test_javascript_protocol(self):
        """Test javascript: protocol detection."""
        payload = "<a href='javascript:alert(1)'>Click</a>"
        assert WAFRules.check_xss(payload) is True

    def test_event_handler(self):
        """Test event handler detection."""
        payload = "<img src=x onerror='alert(1)'>"
        assert WAFRules.check_xss(payload) is True

    def test_iframe_tag(self):
        """Test iframe tag detection."""
        payload = "<iframe src='http://evil.com'></iframe>"
        assert WAFRules.check_xss(payload) is True

    def test_svg_event_handler(self):
        """Test SVG event handler detection."""
        payload = "<svg onload='alert(1)'></svg>"
        assert WAFRules.check_xss(payload) is True

    def test_legitimate_text(self):
        """Test legitimate text is not flagged."""
        payload = "Hello World"
        assert WAFRules.check_xss(payload) is False

    def test_legitimate_html_entity(self):
        """Test legitimate HTML entity is not flagged."""
        payload = "&lt;div&gt;"
        assert WAFRules.check_xss(payload) is False


class TestCommandInjection:
    """Test command injection detection."""

    def test_semicolon_injection(self):
        """Test semicolon command injection."""
        payload = "ls; cat /etc/passwd"
        assert WAFRules.check_command_injection(payload) is True

    def test_pipe_injection(self):
        """Test pipe command injection."""
        payload = "ls | cat /etc/passwd"
        assert WAFRules.check_command_injection(payload) is True

    def test_ampersand_injection(self):
        """Test ampersand command injection."""
        payload = "ls & cat /etc/passwd"
        assert WAFRules.check_command_injection(payload) is True

    def test_backtick_injection(self):
        """Test backtick command injection."""
        payload = "`cat /etc/passwd`"
        assert WAFRules.check_command_injection(payload) is True

    def test_command_substitution(self):
        """Test command substitution injection."""
        payload = "$(cat /etc/passwd)"
        assert WAFRules.check_command_injection(payload) is True

    def test_legitimate_text(self):
        """Test legitimate text is not flagged."""
        payload = "hello world"
        assert WAFRules.check_command_injection(payload) is False


class TestPathTraversal:
    """Test path traversal detection."""

    def test_dot_dot_slash(self):
        """Test ../ path traversal."""
        payload = "../../etc/passwd"
        assert WAFRules.check_path_traversal(payload) is True

    def test_dot_dot_backslash(self):
        """Test ..\\ path traversal."""
        payload = "..\\..\\windows\\system32"
        assert WAFRules.check_path_traversal(payload) is True

    def test_url_encoded_traversal(self):
        """Test URL-encoded path traversal."""
        payload = "%2e%2e/etc/passwd"
        assert WAFRules.check_path_traversal(payload) is True

    def test_legitimate_path(self):
        """Test legitimate path is not flagged."""
        payload = "/home/user/documents"
        assert WAFRules.check_path_traversal(payload) is False


class TestXXEDetection:
    """Test XXE detection."""

    def test_doctype_declaration(self):
        """Test DOCTYPE declaration detection."""
        payload = "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        assert WAFRules.check_xxe(payload) is True

    def test_entity_declaration(self):
        """Test ENTITY declaration detection."""
        payload = "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>"
        assert WAFRules.check_xxe(payload) is True

    def test_system_keyword(self):
        """Test SYSTEM keyword detection."""
        payload = "SYSTEM 'file:///etc/passwd'"
        assert WAFRules.check_xxe(payload) is True

    def test_legitimate_xml(self):
        """Test legitimate XML is not flagged."""
        payload = "<root><item>value</item></root>"
        assert WAFRules.check_xxe(payload) is False


class TestDeserializationDetection:
    """Test insecure deserialization detection."""

    def test_pickle_detection(self):
        """Test pickle detection."""
        payload = "pickle.loads(data)"
        assert WAFRules.check_deserialization(payload) is True

    def test_reduce_detection(self):
        """Test __reduce__ detection."""
        payload = "__reduce__"
        assert WAFRules.check_deserialization(payload) is True

    def test_getstate_detection(self):
        """Test __getstate__ detection."""
        payload = "__getstate__"
        assert WAFRules.check_deserialization(payload) is True

    def test_legitimate_text(self):
        """Test legitimate text is not flagged."""
        payload = "normal data"
        assert WAFRules.check_deserialization(payload) is False


class TestValidateAll:
    """Test validate_all method."""

    def test_clean_data(self):
        """Test clean data passes validation."""
        data = {
            "username": "john",
            "email": "john@example.com",
            "age": 30,
        }
        violations = WAFRules.validate_all(data)
        assert len(violations) == 0

    def test_sql_injection_in_data(self):
        """Test SQL injection in data is detected."""
        data = {
            "username": "admin' OR '1'='1",
            "email": "john@example.com",
        }
        violations = WAFRules.validate_all(data)
        assert len(violations) > 0
        assert any("SQL injection" in v for v in violations)

    def test_xss_in_data(self):
        """Test XSS in data is detected."""
        data = {
            "username": "john",
            "bio": "<script>alert('XSS')</script>",
        }
        violations = WAFRules.validate_all(data)
        assert len(violations) > 0
        assert any("XSS" in v for v in violations)

    def test_nested_injection(self):
        """Test nested injection is detected."""
        data = {
            "user": {
                "profile": {
                    "bio": "<img src=x onerror='alert(1)'>",
                }
            }
        }
        violations = WAFRules.validate_all(data)
        assert len(violations) > 0

    def test_list_injection(self):
        """Test injection in list is detected."""
        data = {
            "tags": ["safe", "<script>alert(1)</script>"],
        }
        violations = WAFRules.validate_all(data)
        assert len(violations) > 0


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_string(self):
        """Test empty string."""
        assert WAFRules.check_sql_injection("") is False
        assert WAFRules.check_xss("") is False

    def test_none_value(self):
        """Test None value."""
        assert WAFRules.check_sql_injection(None) is False
        assert WAFRules.check_xss(None) is False

    def test_numeric_value(self):
        """Test numeric value."""
        assert WAFRules.check_sql_injection(123) is False
        assert WAFRules.check_xss(456) is False

    def test_case_insensitive_detection(self):
        """Test case-insensitive detection."""
        payload_lower = "select * from users"
        payload_upper = "SELECT * FROM USERS"
        assert WAFRules.check_sql_injection(payload_lower) is True
        assert WAFRules.check_sql_injection(payload_upper) is True

    def test_mixed_case_detection(self):
        """Test mixed case detection."""
        payload = "SeLeCt * FrOm users"
        assert WAFRules.check_sql_injection(payload) is True
