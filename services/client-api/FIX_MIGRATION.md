# Fix Migration Error

## Issue
The migration `20241218_t1_business` is trying to create tables that already exist in the database.

## Quick Fix

Since the tables already exist, mark the migration as applied:

```bash
cd services/client-api
alembic stamp 20241218_t1_business
```

This tells Alembic that the migration has been applied without actually running it.

## Alternative: Check Current Migration Status

```bash
cd services/client-api
alembic current
```

## If You Need to Recreate Tables

If you want to drop and recreate the tables:

```bash
# WARNING: This will delete all data!
cd services/client-api
alembic downgrade -1  # Go back one migration
alembic upgrade head  # Apply migrations again
```

## Verify Tables Exist

Check if T1 business form tables exist:

```sql
\dt t1_*
```

You should see:
- t1_forms_main
- t1_personal_info
- t1_spouse_info
- t1_child_info
- t1_foreign_properties
- t1_moving_expenses
- t1_self_employment
- t1_uber_business
- t1_general_business
- t1_rental_income















