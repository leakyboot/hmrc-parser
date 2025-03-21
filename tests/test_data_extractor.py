import pytest
from decimal import Decimal
from app.core.data_extractor import DataExtractor

@pytest.fixture
def data_extractor():
    return DataExtractor()

class TestDataExtractor:
    def test_clean_amount(self, data_extractor):
        """Test cleaning of monetary amounts"""
        test_cases = [
            ("£45,000.00", Decimal("45000.00")),
            ("45,000", Decimal("45000")),
            ("1,234.56", Decimal("1234.56")),
            ("£0.00", Decimal("0.00")),
        ]
        
        for input_str, expected in test_cases:
            assert data_extractor.clean_amount(input_str) == expected

    def test_extract_data_p60(self, data_extractor):
        """Test extraction of data from P60 format"""
        test_text = """
        Tax Year: 2024/25
        Employer: Test Corp Ltd
        Total Pay: £45,000.00
        Tax Paid: £9,000.00
        NI Number: AB 12 34 56 C
        NI contributions: £4,500.00
        """
        
        result = data_extractor.extract_data(test_text, "P60")
        
        assert result["tax_year"] == "2024/25"
        assert result["employer"] == "Test Corp Ltd"
        assert result["total_income"] == Decimal("45000.00")
        assert result["tax_paid"] == Decimal("9000.00")
        assert result["ni_number"] == "AB 12 34 56 C"
        assert result["ni_contributions"] == Decimal("4500.00")

    def test_extract_data_p45(self, data_extractor):
        """Test extraction of data from P45 format"""
        test_text = """
        Tax Year: 2024-2025
        Employer's name: Different Corp
        Total Income: £25,000
        Tax Deducted: £5,000
        National Insurance No: CD 98 76 54 E
        """
        
        result = data_extractor.extract_data(test_text, "P45")
        
        assert result["tax_year"] == "2024-2025"
        assert result["employer"] == "Different Corp"
        assert result["total_income"] == Decimal("25000")
        assert result["tax_paid"] == Decimal("5000")
        assert result["ni_number"] == "CD 98 76 54 E"

    def test_validation_missing_fields(self, data_extractor):
        """Test validation of required fields"""
        test_text = """
        Tax Year: 2024/25
        Total Income: £45,000
        """
        
        with pytest.raises(ValueError) as exc_info:
            data_extractor.extract_data(test_text, "P60")
        assert "Missing required fields" in str(exc_info.value)

    def test_validation_invalid_amounts(self, data_extractor):
        """Test validation of monetary amounts"""
        test_text = """
        Tax Year: 2024/25
        Employer: Test Corp
        Total Income: £5,000
        Tax Paid: £10,000
        """
        
        with pytest.raises(ValueError) as exc_info:
            data_extractor.extract_data(test_text, "P60")
        assert "Tax paid cannot be greater than total income" in str(exc_info.value)

    def test_extract_data_with_different_formats(self, data_extractor):
        """Test extraction with different text formats"""
        test_cases = [
            # Standard format
            ("Tax Year: 2024/25", "2024/25"),
            # Alternative format
            ("Tax Year 2024-2025", "2024-2025"),
            # With extra spaces
            ("Tax  Year:   2024/25  ", "2024/25"),
            # Different employer formats
            ("Employer: Test Corp", "Test Corp"),
            ("Employer's name: Test Corp", "Test Corp"),
            ("EMPLOYER NAME: Test Corp", "Test Corp"),
        ]
        
        for input_text, expected in test_cases:
            # Disable validation since we're testing individual field extraction
            result = data_extractor.extract_data(input_text, "P60", validate=False)
            if "Tax Year" in input_text:
                assert result["tax_year"] == expected
            if "Employer" in input_text or "EMPLOYER" in input_text:
                assert result["employer"] == expected
