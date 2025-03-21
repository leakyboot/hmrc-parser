import re
from decimal import Decimal
from typing import Dict, Any
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DataExtractor:
    # Feature flag for detailed logging
    ENABLE_DEBUG_LOGGING = os.getenv('ENABLE_DEBUG_LOGGING', '').lower() == 'true'

    def _debug_log(self, message: str) -> None:
        """Helper method for feature-flagged debug logging."""
        if self.ENABLE_DEBUG_LOGGING:
            logger.debug(message)

    def clean_amount(self, amount: str) -> Decimal:
        """Clean and convert amount string to Decimal."""
        if not amount:
            return Decimal('0')
        # Remove currency symbols, commas and whitespace
        cleaned = re.sub(r'[£,\s]', '', amount)
        try:
            return Decimal(cleaned)
        except:
            return Decimal('0')

    def extract_data(self, text: str, document_type: str = 'P60', validate: bool = True) -> Dict[str, Any]:
        """Extract structured data from OCR text."""
        data = {}
        self._debug_log(f"Extracting data from text (length: {len(text)})")
        
        # Common patterns
        patterns = {
            'tax_year': r'(?:Tax Year|Year)(?: ending)?(?: 5 April)? (\d{4})',
            'ni_number': r'(?:National Insurance Number|NI Number|NI No)[\s:]*([A-Z]{2}(?:\s*\d{2}){3}\s*[A-Z])',
            'total_pay': r'(?:Total pay(?:ment)?(?:s)?|Pay)[\s:]*[£]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'total_tax': r'(?:Total tax(?:es)?|Tax deducted)[\s:]*[£]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        }

        # Document type specific patterns
        if document_type == 'P60':
            patterns.update({
                'employer_name': r'(?:Employer\'s?|Employer details?)[\s:]*([^\n]+)',
                'employee_name': r'(?:Employee\'s?|Employee details?)[\s:]*([^\n]+)',
            })
        elif document_type == 'P45':
            patterns.update({
                'employer_name': r'(?:Employer name|Employer)[\s:]*([^\n]+)',
                'employee_name': r'(?:Employee|Name)[\s:]*([^\n]+)',
                'leaving_date': r'(?:Date of leaving|Leaving date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                'pay_date': r'(?:Date of payment|Payment date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            })
        else:
            patterns.update({
                'employer_name': r'(?:Employer name|Employer)[\s:]*([^\n]+)',
                'employee_name': r'(?:Employee|Name)[\s:]*([^\n]+)',
            })

        # Extract data using patterns
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key in ['total_pay', 'total_tax']:
                    data[key] = self.clean_amount(value)
                else:
                    data[key] = value
                self._debug_log(f"Found {key}: {value}")
            else:
                self._debug_log(f"No match found for {key}")
                data[key] = None if key not in ['total_pay', 'total_tax'] else Decimal('0')

        # Handle tax year in different formats
        if not data.get('tax_year'):
            self._debug_log("Trying alternative tax year formats")
            # Try alternative formats
            alt_patterns = [
                r'(?:20\d{2})[/-](?:20\d{2})',  # 2022/2023 or 2022-2023
                r'(?:20\d{2})',  # Just the year
            ]
            for pattern in alt_patterns:
                match = re.search(pattern, text)
                if match:
                    year_str = match.group(0)
                    if '/' in year_str or '-' in year_str:
                        # Extract end year from tax year range
                        data['tax_year'] = year_str.split('/')[-1].split('-')[-1]
                    else:
                        # Single year format
                        data['tax_year'] = year_str
                    self._debug_log(f"Found tax year using alternative format: {data['tax_year']}")
                    break

        # Validation
        if validate:
            required_fields = {
                'P60': ['tax_year', 'ni_number', 'total_pay', 'total_tax'],
                'P45': ['tax_year', 'ni_number', 'total_pay', 'total_tax', 'leaving_date']
            }
            
            if document_type in required_fields:
                missing_fields = [field for field in required_fields[document_type] 
                                if field not in data or not data[field]]
                
                if missing_fields:
                    error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                    logger.error(error_msg)  # Always log errors regardless of feature flag
                    raise ValueError(error_msg)

        return data
