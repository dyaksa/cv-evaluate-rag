from __future__ import annotations
import io
from typing import BinaryIO, Union
from pypdf import PdfReader

def extract_text_from_pdf(file: Union[BinaryIO, bytes, str]) -> str:
    """Extract text from a PDF file.

    Args:
        file (Union[BinaryIO, bytes, str]): The PDF file to extract text from. 
            Can be a file-like object, bytes, or a file path.

    Returns:
        str: The extracted text from the PDF.
    """
    if isinstance(file, (bytes, bytearray)):
        pdf_stream = io.BytesIO(file)
        reader = PdfReader(pdf_stream)
    elif hasattr(file, 'read'):
        reader = PdfReader(file)
    elif isinstance(file, str):
        with open(file, 'rb') as f:
            reader = PdfReader(f)
    else:
        raise TypeError("Invalid file type")
    
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
        
    return "\n".join(parts).strip()