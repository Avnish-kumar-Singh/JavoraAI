"""
DSA Models
"""

from dataclasses import dataclass


@dataclass
class DSARequest:
    question: str


@dataclass
class DSAResponse:
    answer: str