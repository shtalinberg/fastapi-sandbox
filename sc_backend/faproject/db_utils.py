#!/usr/bin/env python3
"""
Database migration utilities using Alembic.
This script provides common database operations for development.
"""

import argparse
import asyncio

from sqlalchemy import select

from db.database import async_session_maker
from models import Product, User
from models.user import UserRole


async def create_sample_data():
    """Create sample data for development/testing."""
    print("🧪 Creating sample data...")

    async with async_session_maker() as session:
        # Check if data already exists
        result = await session.execute(select(User))
        if result.scalars().first():
            print("⚠️  Sample data already exists. Skipping...")
            return

        # Create admin user
        admin_user = User(
            email="admin@example.com",
            password=(
                "$2b$12$hashed_password_here"
            ),  # In real app, this would be properly hashed
            role=UserRole.ADMIN,
        )
        session.add(admin_user)
        await session.flush()

        # Create regular user
        regular_user = User(
            email="user@example.com",
            password=("$2b$12$hashed_password_here"),
            role=UserRole.USER,
        )
        session.add(regular_user)
        await session.flush()

        # Create sample products
        products = [
            Product(
                title="Premium Laptop",
                price=1299.99,
                description="High-performance laptop for professionals",
                external_id="ext_laptop_001",
                height=2.0,
                length=35.0,
                depth=25.0,
                owner_id=admin_user.id,
            ),
            Product(
                title="Wireless Mouse",
                price=29.99,
                description="Ergonomic wireless mouse with precision tracking",
                external_id="ext_mouse_001",
                height=4.0,
                length=12.0,
                depth=6.0,
                owner_id=admin_user.id,
            ),
            Product(
                title="Mechanical Keyboard",
                price=89.99,
                description="RGB mechanical keyboard with custom switches",
                external_id="ext_keyboard_001",
                height=3.5,
                length=45.0,
                depth=15.0,
                owner_id=regular_user.id,
            ),
        ]

        for product in products:
            session.add(product)

        await session.commit()
        print("✅ Sample data created successfully!")


async def show_database_status():
    """Show current database status."""
    print("📊 Database Status:")

    async with async_session_maker() as session:
        # Count users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"  👥 Users: {len(users)}")

        for user in users:
            print(f"    - {user.email} ({user.role})")

        # Count products
        result = await session.execute(select(Product))
        products = result.scalars().all()
        print(f"  📦 Products: {len(products)}")

        for product in products:
            print(
                f"    - {product.title} (${product.price}) by user {product.owner_id}"
            )


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Database utilities")
    parser.add_argument(
        "command", choices=["create-sample-data", "status"], help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "create-sample-data":
        asyncio.run(create_sample_data())
    elif args.command == "status":
        asyncio.run(show_database_status())


if __name__ == "__main__":
    main()
