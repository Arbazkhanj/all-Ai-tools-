"""Instamojo Payment Gateway Integration."""

import hashlib
import hmac
import json
import logging
import uuid
from typing import Dict, Optional, Tuple

import requests
from sqlalchemy.orm import Session

from .models import PricingPlan, TransactionStatus, TransactionType, User, WalletTransaction
from .services import WalletService

logger = logging.getLogger(__name__)

# Instamojo Configuration
INSTAMOJO_API_KEY = "01c6b914d4f8e224cb4b6bdceaeb5b77"
INSTAMOJO_AUTH_TOKEN = "d8ea03ef36c426ab2c10891cabd03d8c"
INSTAMOJO_SALT = "4e57693050da4345984d7d1360149032"

# Instamojo API Base URL
# Use test URL for development, production URL for live
INSTAMOJO_BASE_URL = "https://www.instamojo.com/api/1.1"  # Production
# INSTAMOJO_BASE_URL = "https://test.instamojo.com/api/1.1"  # Test

# Domain Configuration
# Change this to your actual domain
BASE_URL = "https://remove.khanjansevakendra.shop"


class InstamojoPayment:
    """Instamojo Payment Gateway Handler."""

    def __init__(self):
        self.api_key = INSTAMOJO_API_KEY
        self.auth_token = INSTAMOJO_AUTH_TOKEN
        self.base_url = INSTAMOJO_BASE_URL
        self.headers = {
            "X-Api-Key": self.api_key,
            "X-Auth-Token": self.auth_token,
            "Content-Type": "application/json",
        }

    def create_payment_link(
        self,
        amount: float,
        purpose: str,
        buyer_name: str,
        email: str,
        phone: Optional[str] = None,
        redirect_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        custom_fields: Optional[Dict] = None,
    ) -> Tuple[bool, Dict]:
        """Create a payment link."""
        try:
            payload = {
                "amount": str(amount),
                "purpose": purpose,
                "buyer_name": buyer_name,
                "email": email,
                "allow_repeated_payments": False,
                "send_email": False,
                "send_sms": False,
            }

            if phone:
                payload["phone"] = phone

            if redirect_url:
                payload["redirect_url"] = redirect_url

            if webhook_url:
                payload["webhook_url"] = webhook_url

            # Add custom fields
            if custom_fields:
                for key, value in custom_fields.items():
                    payload[f"custom_{key}"] = str(value)

            response = requests.post(
                f"{self.base_url}/payment-requests/",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30,
            )

            if response.status_code == 201:
                data = response.json()
                return True, data["payment_request"]
            else:
                logger.error(f"Instamojo error: {response.text}")
                return False, {"error": response.text}

        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            return False, {"error": str(e)}

    def get_payment_status(self, payment_request_id: str) -> Tuple[bool, Dict]:
        """Get payment status."""
        try:
            response = requests.get(
                f"{self.base_url}/payment-requests/{payment_request_id}/",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["payment_request"]
            else:
                logger.error(f"Instamojo error: {response.text}")
                return False, {"error": response.text}

        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return False, {"error": str(e)}

    def verify_webhook(self, data: Dict, mac: str) -> bool:
        """Verify webhook signature."""
        try:
            # Create string to hash
            sorted_keys = sorted(data.keys())
            message = "|".join(str(data[key]) for key in sorted_keys if key != "mac")

            # Generate MAC
            generated_mac = hmac.new(
                INSTAMOJO_SALT.encode(),
                message.encode(),
                hashlib.sha1,
            ).hexdigest()

            return hmac.compare_digest(generated_mac, mac)
        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return False


class PaymentService:
    """Service for handling payments."""

    def __init__(self):
        self.instamojo = InstamojoPayment()

    def create_plan_purchase_payment(
        self,
        db: Session,
        user: User,
        plan: PricingPlan,
        redirect_url: Optional[str] = None,
    ) -> Tuple[bool, Dict]:
        """Create payment for plan purchase."""
        try:
            # Generate unique order ID
            order_id = str(uuid.uuid4())

            # Create payment link
            success, result = self.instamojo.create_payment_link(
                amount=float(plan.price_inr),
                purpose=f"{plan.display_name} - {plan.credits} Credits",
                buyer_name=user.name or "User",
                email=user.email,
                redirect_url=redirect_url or f"{BASE_URL}/dashboard?payment=success",
                custom_fields={
                    "user_id": user.id,
                    "plan_name": plan.name,
                    "order_id": order_id,
                },
            )

            if success:
                return True, {
                    "payment_url": result["longurl"],
                    "payment_request_id": result["id"],
                    "order_id": order_id,
                }
            else:
                return False, result

        except Exception as e:
            logger.error(f"Error creating plan purchase: {e}")
            return False, {"error": str(e)}

    def process_payment_webhook(
        self,
        db: Session,
        data: Dict,
    ) -> Tuple[bool, str]:
        """Process payment webhook."""
        try:
            # Verify webhook
            mac = data.get("mac", "")
            if not self.instamojo.verify_webhook(data, mac):
                return False, "Invalid webhook signature"

            # Extract data
            status = data.get("status")
            payment_request_id = data.get("payment_request_id")
            payment_id = data.get("payment_id")
            custom_fields = {k: v for k, v in data.items() if k.startswith("custom_")}

            user_id = custom_fields.get("custom_user_id")
            plan_name = custom_fields.get("custom_plan_name")

            if not user_id or not plan_name:
                return False, "Missing custom fields"

            if status == "Credit":
                # Payment successful
                from .models import PlanType
                from .services import PlanService

                plan_type = PlanType(plan_name)

                # Add credits to wallet
                success, message = PlanService.purchase_plan(
                    db=db,
                    user_id=int(user_id),
                    plan_type=plan_type,
                    payment_id=payment_id,
                )

                if success:
                    return True, "Payment processed successfully"
                else:
                    return False, message
            else:
                return False, f"Payment status: {status}"

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False, str(e)

    def check_payment_status(
        self,
        db: Session,
        payment_request_id: str,
    ) -> Tuple[bool, Dict]:
        """Check payment status and process if completed."""
        try:
            success, result = self.instamojo.get_payment_status(payment_request_id)

            if not success:
                return False, result

            status = result.get("status")
            payments = result.get("payments", [])

            if status == "Completed" and payments:
                # Payment successful
                payment = payments[0]
                custom_fields = result.get("custom_fields", {})

                user_id = custom_fields.get("user_id")
                plan_name = custom_fields.get("plan_name")

                if user_id and plan_name:
                    from .models import PlanType
                    from .services import PlanService

                    plan_type = PlanType(plan_name)

                    # Add credits to wallet
                    success, message = PlanService.purchase_plan(
                        db=db,
                        user_id=int(user_id),
                        plan_type=plan_type,
                        payment_id=payment["payment_id"],
                    )

                    return success, {
                        "status": "completed",
                        "message": message,
                        "payment_id": payment["payment_id"],
                    }

            return True, {
                "status": status.lower(),
                "payments": payments,
            }

        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return False, {"error": str(e)}


# Global payment service instance
payment_service = PaymentService()
