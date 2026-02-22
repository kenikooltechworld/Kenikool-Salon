"""
Test accounting endpoints
Task 27: Test Accounting Endpoints
"""
import pytest
from datetime import datetime, timedelta, timezone


class TestChartOfAccounts:
    """Test chart of accounts endpoints"""
    
    def test_create_account(self, test_client, auth_headers, test_tenant):
        """Test POST /api/accounting/accounts - create account"""
        response = test_client.post(
            "/api/accounting/accounts",
            headers=auth_headers,
            json={
                "code": "1000",
                "name": "Cash",
                "account_type": "asset",
                "sub_type": "cash",
                "description": "Cash on hand"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "1000"
        assert data["name"] == "Cash"
        assert data["account_type"] == "asset"
    
    def test_get_chart_of_accounts(self, test_client, auth_headers, test_tenant):
        """Test GET /api/accounting/accounts - get chart of accounts"""
        # Create an account first
        test_client.post(
            "/api/accounting/accounts",
            headers=auth_headers,
            json={
                "code": "2000",
                "name": "Accounts Payable",
                "account_type": "liability",
                "sub_type": "accounts_payable",
                "description": "Money owed to suppliers"
            }
        )
        
        response = test_client.get(
            "/api/accounting/accounts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestJournalEntries:
    """Test journal entry endpoints"""
    
    def test_create_journal_entry(self, test_client, auth_headers, test_tenant, test_account):
        """Test POST /api/accounting/journal-entries - create journal entry"""
        response = test_client.post(
            "/api/accounting/journal-entries",
            headers=auth_headers,
            json={
                "date": datetime.now(timezone.utc).isoformat(),
                "description": "Test journal entry",
                "line_items": [
                    {
                        "account_id": test_account["id"],
                        "debit": 1000.0,
                        "credit": 0.0,
                        "description": "Debit entry"
                    },
                    {
                        "account_id": test_account["id"],
                        "debit": 0.0,
                        "credit": 1000.0,
                        "description": "Credit entry"
                    }
                ],
                "reference": "JE-001"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Test journal entry"
        assert len(data["line_items"]) == 2
    
    def test_get_journal_entries(self, test_client, auth_headers, test_tenant):
        """Test GET /api/accounting/journal-entries - list journal entries"""
        response = test_client.get(
            "/api/accounting/journal-entries",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestFinancialReports:
    """Test financial report endpoints"""
    
    def test_generate_balance_sheet(self, test_client, auth_headers, test_tenant):
        """Test POST /api/accounting/reports - generate balance sheet"""
        response = test_client.post(
            "/api/accounting/reports",
            headers=auth_headers,
            json={
                "report_type": "balance_sheet",
                "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_generate_income_statement(self, test_client, auth_headers, test_tenant):
        """Test POST /api/accounting/reports - generate income statement"""
        response = test_client.post(
            "/api/accounting/reports",
            headers=auth_headers,
            json={
                "report_type": "income_statement",
                "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestAccountsReceivable:
    """Test accounts receivable endpoints"""
    
    def test_create_invoice(self, test_client, auth_headers, test_tenant, test_client_fixture):
        """Test POST /api/accounting/receivables - create invoice"""
        response = test_client.post(
            "/api/accounting/receivables",
            headers=auth_headers,
            json={
                "client_id": test_client_fixture["id"],
                "invoice_date": datetime.now(timezone.utc).isoformat(),
                "due_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "line_items": [
                    {
                        "description": "Haircut service",
                        "quantity": 1,
                        "unit_price": 5000.0,
                        "amount": 5000.0
                    }
                ],
                "notes": "Thank you for your business"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == test_client_fixture["id"]
        assert len(data["line_items"]) == 1
    
    def test_get_receivables(self, test_client, auth_headers, test_tenant):
        """Test GET /api/accounting/receivables - list invoices"""
        response = test_client.get(
            "/api/accounting/receivables",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_aging_report(self, test_client, auth_headers, test_tenant):
        """Test GET /api/accounting/receivables/aging - AR aging report"""
        response = test_client.get(
            "/api/accounting/receivables/aging",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
