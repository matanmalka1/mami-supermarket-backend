"""Storefront request schemas."""

from __future__ import annotations

from .common import DefaultModel

class WishlistRequest(DefaultModel):
    product_id: int
