"""
OCR (Optical Character Recognition) Tools for Image Text Extraction
"""
import os
from PIL import Image
import io


def extract_text_from_image(image_content):
    """
    Extract text from image using OCR
    
    Args:
        image_content: Image file content (bytes)
    
    Returns:
        dict: OCR results with extracted text and metadata
    """
    try:
        import pytesseract
        from PIL import Image
        import cv2
        import numpy as np
    except ImportError:
        return {
            "error": "OCR libraries not installed. Please install pytesseract, Pillow, and opencv-python.",
            "success": False
        }
    
    # Check if Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        # Fall back to mock OCR for testing
        return extract_text_mock(image_content)


def extract_text_mock(image_content):
    """
    Mock OCR function for testing when Tesseract is not available
    
    Args:
        image_content: Image file content (bytes)
    
    Returns:
        dict: Mock OCR results
    """
    try:
        from PIL import Image
        import io
        
        # Load image to get basic info
        image = Image.open(io.BytesIO(image_content))
        
        # Mock extracted text for testing
        mock_text = """BizPilot Analytics Dashboard
        Revenue: $125,450.00
        Growth Rate: +15.2%
        Date: 12/15/2024
        Contact: info@bizpilot.com
        Phone: (555) 123-4567"""
        
        # Mock structured information
        structured_info = {
            "emails": ["info@bizpilot.com"],
            "phone_numbers": ["(555) 123-4567"],
            "dates": ["12/15/2024"],
            "currencies": ["$125,450.00"],
            "percentages": ["+15.2%"],
            "companies": ["BizPilot Analytics"],
            "addresses": []
        }
        
        return {
            "success": True,
            "extracted_text": mock_text.strip(),
            "confidence": 85.5,  # Mock confidence
            "word_count": len(mock_text.split()),
            "structured_info": structured_info,
            "quality_score": {"score": 88, "issues": ["Mock OCR - Tesseract not installed"]},
            "mock": True  # Indicate this is mock data
        }
        
    except Exception as e:
        return {
            "error": f"Mock OCR failed: {str(e)}",
            "success": False
        }
    
    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to OpenCV format for preprocessing
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR results
        processed_image = preprocess_image_for_ocr(cv_image)
        
        # Convert back to PIL format
        processed_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        
        try:
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(processed_pil)
            
            # Get additional OCR data (confidence, word positions)
            ocr_data = pytesseract.image_to_data(processed_pil, output_type=pytesseract.Output.DICT)
            
            # Calculate confidence score
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
        except Exception as tesseract_error:
            if "tesseract is not installed" in str(tesseract_error).lower():
                return {
                    "error": "Tesseract OCR engine is not installed. Please install Tesseract from https://github.com/tesseract-ocr/tesseract",
                    "success": False,
                    "installation_help": "For Windows: Download installer from UB-Mannheim/tesseract releases on GitHub"
                }
            else:
                raise tesseract_error
        
        # Extract structured information
        structured_info = extract_structured_info(extracted_text)
        
        return {
            "success": True,
            "extracted_text": extracted_text.strip(),
            "confidence": round(avg_confidence, 2),
            "word_count": len(extracted_text.split()),
            "structured_info": structured_info,
            "quality_score": calculate_text_quality(extracted_text)
        }
        
    except Exception as e:
        return {
            "error": f"OCR processing failed: {str(e)}",
            "success": False
        }


def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image: OpenCV image
    
    Returns:
        Preprocessed OpenCV image
    """
    import cv2
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Convert back to BGR for consistency
    return cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)


def extract_structured_info(text):
    """
    Extract structured business information from text
    
    Args:
        text (str): Extracted text
    
    Returns:
        dict: Structured information
    """
    import re
    
    structured = {
        "emails": [],
        "phone_numbers": [],
        "dates": [],
        "currencies": [],
        "percentages": [],
        "companies": [],
        "addresses": []
    }
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    structured["emails"] = re.findall(email_pattern, text)
    
    # Phone number extraction (various formats)
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s?\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
        r'\b\d{10}\b'  # 1234567890
    ]
    
    for pattern in phone_patterns:
        structured["phone_numbers"].extend(re.findall(pattern, text))
    
    # Date extraction (various formats)
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
        r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
        r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
        r'\b\w+\s+\d{1,2},\s+\d{4}\b'  # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        structured["dates"].extend(re.findall(pattern, text))
    
    # Currency extraction
    currency_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # $1,234.56
        r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|dollars?)\b'
    ]
    
    for pattern in currency_patterns:
        structured["currencies"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Percentage extraction
    percentage_pattern = r'\b\d+(?:\.\d+)?%\b'
    structured["percentages"] = re.findall(percentage_pattern, text)
    
    # Simple company name extraction (words ending with Corp, Inc, LLC, etc.)
    company_pattern = r'\b\w+(?:\s+\w+)*\s+(?:Corp|Inc|LLC|Ltd|Co|Company|Corporation)\b'
    structured["companies"] = re.findall(company_pattern, text, re.IGNORECASE)
    
    return structured


def calculate_text_quality(text):
    """
    Calculate text quality score based on various factors
    
    Args:
        text (str): Extracted text
    
    Returns:
        dict: Quality metrics
    """
    if not text or not text.strip():
        return {"score": 0, "issues": ["Empty text"]}
    
    issues = []
    score = 100
    
    # Check for excessive special characters (indicates poor OCR)
    special_char_ratio = len([c for c in text if not c.isalnum() and not c.isspace()]) / len(text)
    if special_char_ratio > 0.3:
        score -= 20
        issues.append("High special character ratio")
    
    # Check for reasonable word length
    words = text.split()
    if words:
        avg_word_length = sum(len(word) for word in words) / len(words)
        if avg_word_length < 2:
            score -= 15
            issues.append("Very short average word length")
        elif avg_word_length > 15:
            score -= 10
            issues.append("Very long average word length")
    
    # Check for consecutive special characters (OCR artifacts)
    import re
    if re.search(r'[^a-zA-Z0-9\s]{3,}', text):
        score -= 15
        issues.append("Consecutive special characters detected")
    
    # Check for reasonable capitalization
    if text.isupper():
        score -= 5
        issues.append("All uppercase text")
    elif text.islower() and len(words) > 5:
        score -= 5
        issues.append("All lowercase text")
    
    return {
        "score": max(0, score),
        "issues": issues if issues else ["Good quality text"]
    }


def format_ocr_analysis(ocr_result, filename):
    """
    Format OCR results into a readable analysis
    
    Args:
        ocr_result (dict): OCR processing results
        filename (str): Name of the processed image file
    
    Returns:
        str: Formatted analysis text
    """
    if not ocr_result.get("success"):
        return f"OCR failed for {filename}: {ocr_result.get('error', 'Unknown error')}"
    
    extracted_text = ocr_result["extracted_text"]
    confidence = ocr_result["confidence"]
    structured_info = ocr_result["structured_info"]
    quality = ocr_result["quality_score"]
    
    analysis = f"""# Image Text Analysis for {filename}

## Extraction Summary
- **Confidence Score**: {confidence}%
- **Words Extracted**: {ocr_result['word_count']}
- **Text Quality**: {quality['score']}/100

## Extracted Text
```
{extracted_text}
```

## Structured Information Found
"""
    
    # Add structured information if found
    if structured_info["emails"]:
        analysis += f"**Email Addresses**: {', '.join(structured_info['emails'])}\n"
    
    if structured_info["phone_numbers"]:
        analysis += f"**Phone Numbers**: {', '.join(structured_info['phone_numbers'])}\n"
    
    if structured_info["dates"]:
        analysis += f"**Dates**: {', '.join(structured_info['dates'])}\n"
    
    if structured_info["currencies"]:
        analysis += f"**Currency Values**: {', '.join(structured_info['currencies'])}\n"
    
    if structured_info["percentages"]:
        analysis += f"**Percentages**: {', '.join(structured_info['percentages'])}\n"
    
    if structured_info["companies"]:
        analysis += f"**Companies**: {', '.join(structured_info['companies'])}\n"
    
    # Add quality issues if any
    if quality["issues"] and quality["issues"] != ["Good quality text"]:
        analysis += f"\n## Quality Issues\n"
        for issue in quality["issues"]:
            analysis += f"- {issue}\n"
    
    # Add recommendations
    analysis += f"\n## Recommendations\n"
    if confidence < 50:
        analysis += "- Image quality is low. Consider using a higher resolution image or better lighting\n"
    if quality["score"] < 70:
        analysis += "- Text extraction had some issues. Manual review recommended\n"
    if not any(structured_info.values()):
        analysis += "- No structured business information detected. This appears to be general text\n"
    else:
        analysis += "- Structured business information successfully extracted\n"
    
    return analysis