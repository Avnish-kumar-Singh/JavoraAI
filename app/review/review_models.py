"""
Review Models
"""

from dataclasses import dataclass


@dataclass
class ReviewRequest:
    code: str


@dataclass
class ReviewResponse:
    review: str