#!/usr/bin/env python3
"""
Demo: Tìm áo thun + nước uống với skill bi193-shopping
"""

import json

def demo_shopping():
    """Demo workflow mua áo thun + nước uống"""
    
    print("\n" + "="*70)
    print("🛍️  SKILL BI193-SHOPPING: Mua áo thun + nước uống")
    print("="*70)
    
    # ─────────────────────────────────────────────────────────────
    # [1] TÌM KIẾM: Áo thun
    # ─────────────────────────────────────────────────────────────
    print("\n[1] 🔍 TÌM KIẾM ÁO THUN (tee shirt)")
    print("-" * 70)
    
    tee_search = "tee shirt"
    print(f"   Tool: open_product_explorer(search='{tee_search}', first=10)")
    print(f"""
   UI mở:
   ┌────────────────────────────────────────────────────────────┐
   │  🛍️  PRODUCTS — Tee Shirts                              │
   ├────────────────────────────────────────────────────────────┤
   │  □ Saleor T-Shirt  (5.99 USD)  ⭐⭐⭐⭐⭐ Còn hàng ✓      │
   │  □ Blue Polygon Tee (7.99 USD) ⭐⭐⭐⭐☆ Còn hàng ✓      │
   │  □ Team Tee  (6.49 USD) ⭐⭐⭐⭐⭐ Còn hàng ✓           │
   │  □ ASCII Shirt  (8.99 USD) ⭐⭐⭐⭐☆ Còn hàng ✓         │
   └────────────────────────────────────────────────────────────┘
   """)
    
    print("   ✅ Tìm được 4 áo thun")
    
    # ─────────────────────────────────────────────────────────────
    # [2] TÌM KIẾM: Nước uống
    # ─────────────────────────────────────────────────────────────
    print("\n[2] 🔍 TÌM KIẾM NƯỚC UỐNG (beverages)")
    print("-" * 70)
    
    drink_search = "beverages drink"
    print(f"   Tool: open_product_explorer(search='{drink_search}', first=10)")
    print(f"""
   UI mở:
   ┌────────────────────────────────────────────────────────────┐
   │  🛍️  PRODUCTS — Beverages & Drinks                     │
   ├────────────────────────────────────────────────────────────┤
   │  □ Coffee Blend  (3.99 USD)  ⭐⭐⭐⭐⭐ Còn 50 cái        │
   │  □ Fresh Juice  (2.49 USD) ⭐⭐⭐⭐☆ Còn 120 cái       │
   │  □ Green Tea  (4.99 USD) ⭐⭐⭐⭐⭐ Còn 80 cái          │
   │  □ Energy Drink  (5.99 USD) ⭐⭐⭐⭐☆ Còn 100 cái      │
   └────────────────────────────────────────────────────────────┘
   """)
    
    print("   ✅ Tìm được 4 nước uống")
    
    # ─────────────────────────────────────────────────────────────
    # [3] THÊM VÀO GIỎ: Áo thun (2 cái)
    # ─────────────────────────────────────────────────────────────
    print("\n[3] 🛒 THÊM VÀO GIỎ: 2 cái áo thun")
    print("-" * 70)
    
    print(f"""
   Bước 1: create_cart(channel='default-channel', email='user@shop.com')
   → Checkout ID: checkout_abc123xyz
   
   Bước 2: add_to_cart(checkout_id='checkout_abc123xyz', lines=[
       {{"quantity": 2, "variantId": "UHJvZHVjdFZhcmlhbnQ6MQ=="}} // Áo thun
   ])
   """)
    
    print("   ✅ Đã thêm 2 cái áo thun vào giỏ (2 x $6.49 = $12.98)")
    
    # ─────────────────────────────────────────────────────────────
    # [4] THÊM VÀO GIỎ: Nước uống (1 cái)
    # ─────────────────────────────────────────────────────────────
    print("\n[4] 🛒 THÊM VÀO GIỎ: 1 cái nước uống")
    print("-" * 70)
    
    print(f"""
   Bước: add_to_cart(checkout_id='checkout_abc123xyz', lines=[
       {{"quantity": 1, "variantId": "UHJvZHVjdFZhcmlhbnQ6NQ=="}} // Nước uống
   ])
   """)
    
    print("   ✅ Đã thêm 1 cái nước uống vào giỏ (1 x $3.99 = $3.99)")
    
    # ─────────────────────────────────────────────────────────────
    # [5] XEM GIỎ HÀM
    # ─────────────────────────────────────────────────────────────
    print("\n[5] 👁️  XEM GIỎ HÀNG")
    print("-" * 70)
    
    print(f"""
   Tool: open_cart(checkout_id='checkout_abc123xyz')
   
   UI:
   ┌─────────────────────────────────────────────────────────────┐
   │  🛒 GIỎ HÀNG                                                 │
   ├─────────────────────────────────────────────────────────────┤
   │  • Saleor T-Shirt (x2) ............... $12.98               │
   │  • Coffee Blend (x1) ................ $ 3.99               │
   ├─────────────────────────────────────────────────────────────┤
   │  Subtotal: $16.97                                           │
   │  Shipping: (chưa chọn)                                      │
   │  Tax: —                                                     │
   │  ────────────────────                                       │
   │  TOTAL: $16.97                                              │
   │                                                              │
   │  [ THANH TOÁN ]                                             │
   └─────────────────────────────────────────────────────────────┘
   """)
    
    print("   ✅ Giỏ hàng sẵn sàng thanh toán")
    
    # ─────────────────────────────────────────────────────────────
    # [6] CHECKOUT
    # ─────────────────────────────────────────────────────────────
    print("\n[6] 💳 THANH TOÁN")
    print("-" * 70)
    
    print(f"""
   Tool: open_checkout(checkout_id='checkout_abc123xyz',
       first_name='Nguyễn', last_name='Văn A',
       street_address='123 Nguyễn Huệ', city='Ho Chi Minh',
       postal_code='70000', country='VN'
   )
   
   UI: Form thanh toán mở
   → Người dùng chọn shipping method
   → Chọn payment gateway
   → Xác nhận và thanh toán
   
   ✅ Đơn hàng tạo thành công!
   Order ID: #12345 | Total: $16.97
   """)
    
    print("\n" + "="*70)
    print("✅ HOÀN TẤT!")
    print("="*70)
    
    print("""
    📋 NGUYÊN TẮC SKILL BI193-SHOPPING:
    
    ✓ DISCOVER (Tìm kiếm)
      → Dùng open_product_explorer (UI-first)
      → Search keywords tiếng Anh: 'tee shirt', 'beverage'
    
    ✓ CART (Thêm vào giỏ)
      → create_cart → add_to_cart → open_cart
      → Không dump JSON — UI đã hiển thị
    
    ✓ CHECKOUT (Thanh toán)
      → open_checkout → set_shipping_address → set_shipping_method
      → create_payment → complete_checkout
    
    ✓ TRACK (Theo dõi)
      → track_order → xem fulfillment status
    """)

if __name__ == "__main__":
    demo_shopping()
