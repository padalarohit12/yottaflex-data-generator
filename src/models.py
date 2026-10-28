"""
Data models and enums
"""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SellerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"

class OrderStatus(str, Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class FulfillmentStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    RETURNED = "RETURNED"
    FAILED = "FAILED"

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED_SELLER = "RESOLVED_SELLER"
    RESOLVED_CUSTOMER = "RESOLVED_CUSTOMER"
    CHARGEBACK = "CHARGEBACK"
    CLOSED = "CLOSED"

class PayoutStatus(str, Enum):
    PENDING = "PENDING"
    HELD = "HELD"
    ELIGIBLE = "ELIGIBLE"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class PayoutLineStatus(str, Enum):
    PENDING = "PENDING"
    HELD = "HELD"
    ELIGIBLE = "ELIGIBLE"
    PAID = "PAID"
    ADJUSTED = "ADJUSTED"

ALLOWED_TRANSITIONS = {
    OrderStatus: {
        OrderStatus.CREATED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
        OrderStatus.COMPLETED: [],
        OrderStatus.CANCELLED: [],
    },
    FulfillmentStatus: {
        FulfillmentStatus.PENDING: [FulfillmentStatus.SHIPPED, FulfillmentStatus.FAILED],
        FulfillmentStatus.SHIPPED: [FulfillmentStatus.IN_TRANSIT, FulfillmentStatus.FAILED],
        FulfillmentStatus.IN_TRANSIT: [FulfillmentStatus.DELIVERED, FulfillmentStatus.FAILED],
        FulfillmentStatus.DELIVERED: [FulfillmentStatus.RETURNED],
        FulfillmentStatus.RETURNED: [],
        FulfillmentStatus.FAILED: [],
    },
    DisputeStatus: {
        DisputeStatus.OPEN: [DisputeStatus.UNDER_REVIEW],
        DisputeStatus.UNDER_REVIEW: [DisputeStatus.RESOLVED_SELLER, DisputeStatus.RESOLVED_CUSTOMER, DisputeStatus.CHARGEBACK],
        DisputeStatus.RESOLVED_SELLER: [DisputeStatus.CLOSED],
        DisputeStatus.RESOLVED_CUSTOMER: [DisputeStatus.CLOSED],
        DisputeStatus.CHARGEBACK: [DisputeStatus.CLOSED],
        DisputeStatus.CLOSED: [],
    },
    PayoutStatus: {
        PayoutStatus.PENDING: [PayoutStatus.HELD, PayoutStatus.ELIGIBLE],
        PayoutStatus.HELD: [PayoutStatus.ELIGIBLE],
        PayoutStatus.ELIGIBLE: [PayoutStatus.PROCESSING],
        PayoutStatus.PROCESSING: [PayoutStatus.PAID],
        PayoutStatus.PAID: [],
        PayoutStatus.CANCELLED: [],
    }
}
