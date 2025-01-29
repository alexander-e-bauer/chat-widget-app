import os
import re
import logging
from typing import Dict, List, Optional, Tuple
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile


class PaystubProcessor:
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Add file handler for logging
        fh = logging.FileHandler('logs/paystub_processor.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)

    def process_paystub(self, file_path: str) -> Optional[Dict[str, float]]:
        """
        Process a paystub file and extract relevant information.

        :param file_path: Path to the paystub file (PDF or image)
        :return: Dictionary with extracted information or None if processing fails
        """
        try:
            # Convert PDF to images if necessary
            if file_path.lower().endswith('.pdf'):
                images = self._pdf_to_images(file_path)
            else:
                images = [Image.open(file_path)]

            # Extract text from images
            full_text = ""
            for img in images:
                full_text += pytesseract.image_to_string(img)

            # Extract relevant information
            gross_pay = self._extract_amount(full_text, r'Gross Pay.*?(\d+\.\d{2})')
            net_pay = self._extract_amount(full_text, r'Net Pay.*?(\d+\.\d{2})')

            # Extract deductions
            deductions = self._extract_deductions(full_text)

            result = {
                'gross_pay': gross_pay,
                'net_pay': net_pay,
                'deductions': deductions
            }

            self.logger.info(f"Successfully processed paystub: {file_path}")
            return result

        except Exception as e:
            self.logger.error(f"Error processing paystub {file_path}: {str(e)}")
            return None

    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF to list of PIL Image objects."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(pdf_path, output_folder=temp_dir)
            return images
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {str(e)}")
            raise

    def _extract_amount(self, text: str, pattern: str) -> Optional[float]:
        """Extract amount using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                self.logger.warning(f"Failed to convert extracted amount to float: {match.group(1)}")
        return None

    def _extract_deductions(self, text: str) -> Dict[str, float]:
        """Extract all deductions from the text."""
        deductions = {}
        deduction_pattern = r'(\w+(?:\s+\w+)*)\s+(-?\d+\.\d{2})'
        matches = re.findall(deduction_pattern, text)
        for name, amount in matches:
            try:
                deductions[name.strip()] = float(amount)
            except ValueError:
                self.logger.warning(f"Failed to convert deduction amount to float: {amount}")
        return deductions

    def calculate_total_deductions(self, deductions: Dict[str, float]) -> float:
        """Calculate the total of all deductions."""
        return sum(deductions.values())

    def verify_paystub(self, paystub_data: Dict[str, float]) -> Tuple[bool, str]:
        """
        Verify the paystub data for consistency.

        :param paystub_data: Dictionary containing paystub information
        :return: Tuple of (is_valid, message)
        """
        gross_pay = paystub_data.get('gross_pay')
        net_pay = paystub_data.get('net_pay')
        deductions = paystub_data.get('deductions', {})

        if gross_pay is None or net_pay is None:
            return False, "Missing gross pay or net pay information"

        total_deductions = self.calculate_total_deductions(deductions)
        calculated_net_pay = gross_pay - total_deductions

        # Allow for small discrepancies due to rounding
        if abs(calculated_net_pay - net_pay) < 0.01:
            return True, "Paystub verified successfully"
        else:
            return False, f"Discrepancy found: Calculated net pay ({calculated_net_pay:.2f}) " \
                          f"does not match reported net pay ({net_pay:.2f})"

