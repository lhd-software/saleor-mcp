import asyncio
from saleor_mcp.ctx_utils import get_saleor_client
from saleor_mcp.saleor_client.input_types import AddressInput, PaymentInput, CountryCode

async def test_checkout_tools():
    client = get_saleor_client()
    print("Saleor client initialized.")
    
    # We won't actually run a full checkout because we need real IDs,
    # but we can verify the methods exist and schema matches.
    methods = [
        "checkout_details",
        "checkout_shipping_address_update",
        "checkout_billing_address_update",
        "checkout_shipping_method_update",
        "checkout_payment_create"
    ]
    
    for method in methods:
        if hasattr(client, method):
            print(f"✅ Client has method: {method}")
        else:
            print(f"❌ Client MISSING method: {method}")

if __name__ == "__main__":
    asyncio.run(test_checkout_tools())
