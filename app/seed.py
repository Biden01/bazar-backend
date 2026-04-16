"""Seed data mirroring bazar-mobile/data/mock.ts"""
import asyncio
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models import *


async def seed():
    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(User))
        if result.scalars().first():
            print("Database already seeded, skipping.")
            return

        # --- Users ---
        serik = User(id=1, phone="+77001111111", name="Серик", role="seller", location="Акбулак базар")
        aigul = User(id=2, phone="+77002222222", name="Айгуль", role="seller", location="Ауыл Береке")
        marat = User(id=3, phone="+77003333333", name="Марат", role="seller", location="Акбулак")
        danial = User(id=4, phone="+77004444444", name="Даниял", role="seller", location="Ауыл Береке")
        aliya = User(id=5, phone="+77005555555", name="Алия", role="seller", location="Ауыл Береке")
        buyer1 = User(id=6, phone="+77006666666", name='Ресторан "Алем"', role="b2b")
        buyer2 = User(id=7, phone="+77007777777", name='Тойхана "Салтанат"', role="b2b")
        buyer3 = User(id=8, phone="+77008888888", name='Кафе "Достар"', role="buyer")
        buyer4 = User(id=9, phone="+77009999999", name="Марат (покупатель)", role="buyer")

        db.add_all([serik, aigul, marat, danial, aliya, buyer1, buyer2, buyer3, buyer4])
        await db.flush()

        # --- Products ---
        products = [
            Product(id=1, seller_id=1, name="Говядина — вырезка", category="Мясо", price=2800, wholesale_price=2600, unit="кг", stock=150, min_order=5, rating=4.8, review_count=234),
            Product(id=2, seller_id=2, name="Картофель отборный", category="Овощи/Фрукты", price=170, wholesale_price=150, unit="кг", stock=800, min_order=10, rating=4.9, review_count=189),
            Product(id=3, seller_id=3, name="Баранина свежая", category="Мясо", price=3200, wholesale_price=3000, unit="кг", stock=85, min_order=5, rating=4.7, review_count=156),
            Product(id=4, seller_id=5, name="Курица домашняя", category="Мясо", price=1800, wholesale_price=1600, unit="кг", stock=12, min_order=2, rating=4.7, review_count=98),
            Product(id=5, seller_id=3, name="Лук репчатый", category="Овощи/Фрукты", price=200, wholesale_price=170, unit="кг", stock=500, min_order=5, rating=4.8, review_count=87),
            Product(id=6, seller_id=1, name="Морковь", category="Овощи/Фрукты", price=250, wholesale_price=220, unit="кг", stock=200, min_order=5, rating=4.7, review_count=65),
            Product(id=7, seller_id=4, name="Мука в/с 50кг", category="Мука/Бакалея", price=8500, wholesale_price=8000, unit="мешок", stock=40, min_order=1, rating=4.6, review_count=112),
            Product(id=8, seller_id=4, name="Сахар 50кг", category="Мука/Бакалея", price=12000, wholesale_price=11000, unit="мешок", stock=25, min_order=1, rating=4.5, review_count=78),
        ]
        db.add_all(products)
        await db.flush()

        # --- Inventory (Серик's warehouse) ---
        inventory_items = [
            Inventory(seller_id=1, name="Говядина — вырезка", category="Мясо", price=2800, unit="кг", stock=150, min_stock=20, is_public=True, is_active=True, image_url="🥩"),
            Inventory(seller_id=1, name="Баранина свежая", category="Мясо", price=3200, unit="кг", stock=85, min_stock=15, is_public=True, is_active=True, image_url="🍖"),
            Inventory(seller_id=1, name="Курица домашняя", category="Мясо", price=1800, unit="кг", stock=12, min_stock=10, is_public=True, is_active=True, image_url="🍗"),
            Inventory(seller_id=1, name="Говядина — грудинка", category="Мясо", price=2400, unit="кг", stock=35, min_stock=10, is_public=False, is_active=True, image_url="🥩"),
            Inventory(seller_id=1, name="Конина", category="Мясо", price=3500, unit="кг", stock=0, min_stock=10, is_public=False, is_active=False, image_url="🐴"),
        ]
        db.add_all(inventory_items)

        # --- Debts ---
        debt1 = Debt(id=1, seller_id=1, buyer_name='Ресторан "Алем"', amount=142000, paid_amount=80000, status="partial", description="Говядина 50кг, Баранина 20кг", due_date=date(2024, 2, 20))
        debt2 = Debt(id=2, seller_id=1, buyer_name='Тойхана "Салтанат"', amount=95000, paid_amount=0, status="pending", description="Говядина 25кг, Курица 15кг", due_date=date(2024, 2, 28))
        debt3 = Debt(id=3, seller_id=1, buyer_name='Кафе "Достар"', amount=56000, paid_amount=56000, status="paid", description="Баранина 15кг, Говядина 5кг", due_date=date(2024, 2, 15))
        debt4 = Debt(id=4, seller_id=1, buyer_name="Марат", amount=28000, paid_amount=0, status="overdue", description="Говядина 10кг", due_date=date(2024, 2, 1))
        db.add_all([debt1, debt2, debt3, debt4])
        await db.flush()

        # Debt payments
        db.add_all([
            DebtPayment(debt_id=1, amount=50000, date=date(2024, 1, 25)),
            DebtPayment(debt_id=1, amount=30000, date=date(2024, 2, 1)),
            DebtPayment(debt_id=3, amount=56000, date=date(2024, 2, 10)),
        ])

        # --- Notifications ---
        db.add_all([
            Notification(user_id=6, type="order", title="Заказ подтвержден", message="Продавец Серик подтвердил ваш заказ на 15 кг говядины", is_read=False),
            Notification(user_id=6, type="message", title="Новое сообщение", message='Айгуль: "Сегодня будем работать до 19:00"', is_read=False),
            Notification(user_id=6, type="burning", title="Горящий лот!", message="Картофель по 120₸/кг — осталось 5 минут", is_read=True),
            Notification(user_id=6, type="review", title="Новый отзыв", message='Покупатель оставил отзыв: "Отличное качество! 5 звёзд"', is_read=True),
            Notification(user_id=6, type="order", title="Заказ выполнен", message="Заказ #4521 успешно доставлен", is_read=True),
        ])

        # --- Chat ---
        chat = Chat(buyer_id=6, seller_id=1, last_message_at=datetime.now(timezone.utc))
        db.add(chat)
        await db.flush()

        db.add_all([
            Message(chat_id=chat.id, sender_id=6, text="Салем! У вас есть свежая вырезка?"),
            Message(chat_id=chat.id, sender_id=1, text="Ассалаумағалейкум! Иә, жаңа келді. Қанша керек?"),
            Message(chat_id=chat.id, sender_id=6, text="Нужно 15 кг. Какая цена?"),
            Message(chat_id=chat.id, sender_id=1, text="15 кг — 2700₸ за кг. Оптом беремін."),
            Message(chat_id=chat.id, sender_id=6, text="Хорошо, сегодня заберу. До 17:00 будете?"),
            Message(chat_id=chat.id, sender_id=1, text="Әрине! Жұмыс 18:00 дейін. Келіңіз 👍"),
        ])

        # --- Price Groups ---
        pg1 = PriceGroup(id=1, name="Рестораны", discount_percent=10, description="Скидка для проверенных ресторанов")
        pg2 = PriceGroup(id=2, name="Тойханы", discount_percent=15, description="Максимальная скидка для тойхан")
        pg3 = PriceGroup(id=3, name="Магазины", discount_percent=5, description="Базовая оптовая скидка")
        db.add_all([pg1, pg2, pg3])
        await db.flush()

        # Price group products
        db.add_all([
            PriceGroupProduct(price_group_id=1, product_id=1, special_price=2520),
            PriceGroupProduct(price_group_id=1, product_id=3, special_price=2880),
            PriceGroupProduct(price_group_id=1, product_id=4, special_price=1620),
            PriceGroupProduct(price_group_id=2, product_id=1, special_price=2380),
            PriceGroupProduct(price_group_id=2, product_id=3, special_price=2720),
            PriceGroupProduct(price_group_id=2, product_id=4, special_price=1530),
            PriceGroupProduct(price_group_id=3, product_id=1, special_price=2660),
            PriceGroupProduct(price_group_id=3, product_id=3, special_price=3040),
        ])

        # Price group members
        db.add_all([
            PriceGroupMember(price_group_id=1, user_id=6),  # Ресторан "Алем" -> Рестораны
            PriceGroupMember(price_group_id=2, user_id=7),  # Тойхана "Салтанат" -> Тойханы
        ])

        # --- Vet Certs ---
        db.add_all([
            VetCert(seller_id=1, number="ВСД-2024-001234", product="Говядина свежая", issue_date=date(2024, 1, 25), expiry_date=date(2024, 2, 1), issuer="Ветеринарная служба г. Тараз", status="valid"),
            VetCert(seller_id=3, number="ВСД-2024-001189", product="Баранина", issue_date=date(2024, 1, 20), expiry_date=date(2024, 1, 27), issuer="Ветеринарная служба г. Тараз", status="expiring"),
            VetCert(seller_id=5, number="ВСД-2023-009876", product="Курица", issue_date=date(2024, 1, 15), expiry_date=date(2024, 1, 22), issuer="Ветеринарная служба г. Тараз", status="expired"),
        ])

        # --- Invoices ---
        db.add_all([
            Invoice(seller_id=1, buyer_id=8, number="НАК-2024-456", date=date(2024, 1, 28), amount=142000, item_count=3, status="paid"),
            Invoice(seller_id=2, buyer_id=7, number="НАК-2024-455", date=date(2024, 1, 27), amount=85600, item_count=2, status="pending"),
            Invoice(seller_id=3, buyer_id=6, number="НАК-2024-442", date=date(2024, 1, 25), amount=96000, item_count=4, status="paid"),
        ])

        await db.commit()
        print("Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
