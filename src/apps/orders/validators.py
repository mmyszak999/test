from rest_framework.serializers import ValidationError


def validate_item_quantity(quantity: int, max_quantity: int):
    if quantity > max_quantity:
        raise ValidationError(
            {"quantity": "not enough available products in stock"},
        )


def validate_coupon_total(total: int, min_total: int):
    if total < min_total:
        raise ValidationError({"coupon": "Order total is too low to use this coupon."})


def validate_coupon(amount: int, min_total: int):
    if min_total <= amount:
        raise ValidationError(
            {
                "min_order_total": "Minimal order total must be bigger than the coupon amount"
            }
        )
