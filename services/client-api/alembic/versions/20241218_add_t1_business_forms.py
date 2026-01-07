"""Add T1 Business Forms tables

Revision ID: 20241218_t1_business
Revises: 20251107_t1_forms
Create Date: 2024-12-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20241218_t1_business'
down_revision = '68aa2ca60ef1'  # This is the revision ID from 20251107_0036 migration
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables already exist (for cases where tables were created manually)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Create t1_forms_main table
    if 't1_forms_main' not in existing_tables:
        op.create_table(
            't1_forms_main',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('has_foreign_property', sa.Boolean(), nullable=True),
        sa.Column('has_medical_expenses', sa.Boolean(), nullable=True),
        sa.Column('has_charitable_donations', sa.Boolean(), nullable=True),
        sa.Column('has_moving_expenses', sa.Boolean(), nullable=True),
        sa.Column('is_self_employed', sa.Boolean(), nullable=True),
        sa.Column('is_first_home_buyer', sa.Boolean(), nullable=True),
        sa.Column('sold_property_long_term', sa.Boolean(), nullable=True),
        sa.Column('sold_property_short_term', sa.Boolean(), nullable=True),
        sa.Column('has_work_from_home_expense', sa.Boolean(), nullable=True),
        sa.Column('was_student_last_year', sa.Boolean(), nullable=True),
        sa.Column('is_union_member', sa.Boolean(), nullable=True),
        sa.Column('has_daycare_expenses', sa.Boolean(), nullable=True),
        sa.Column('is_first_time_filer', sa.Boolean(), nullable=True),
        sa.Column('has_other_income', sa.Boolean(), nullable=True),
        sa.Column('other_income_description', sa.Text(), nullable=True),
        sa.Column('has_professional_dues', sa.Boolean(), nullable=True),
        sa.Column('has_rrsp_fhsa_investment', sa.Boolean(), nullable=True),
        sa.Column('has_child_art_sport_credit', sa.Boolean(), nullable=True),
        sa.Column('is_province_filer', sa.Boolean(), nullable=True),
        sa.Column('uploaded_documents', postgresql.JSON(), server_default='{}'),
        sa.Column('awaiting_documents', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_t1_forms_main_user_id', 't1_forms_main', ['user_id'])
    
    # Create t1_personal_info table
    op.create_table(
        't1_personal_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('sin', sa.String(20), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('is_canadian_citizen', sa.Boolean(), nullable=True),
        sa.Column('marital_status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_spouse_info table
    op.create_table(
        't1_spouse_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('personal_info_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('sin', sa.String(20), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['personal_info_id'], ['t1_personal_info.id'], ondelete='CASCADE'),
    )
    
    # Create t1_child_info table
    op.create_table(
        't1_child_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('personal_info_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('sin', sa.String(20), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['personal_info_id'], ['t1_personal_info.id'], ondelete='CASCADE'),
    )
    
    # Create t1_foreign_properties table
    op.create_table(
        't1_foreign_properties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False),
        sa.Column('investment_details', sa.Text(), nullable=True),
        sa.Column('gross_income', sa.Float(), server_default='0.0'),
        sa.Column('gain_loss_on_sale', sa.Float(), server_default='0.0'),
        sa.Column('max_cost_during_year', sa.Float(), server_default='0.0'),
        sa.Column('cost_amount_year_end', sa.Float(), server_default='0.0'),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_moving_expenses table
    op.create_table(
        't1_moving_expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False, unique=True),
        sa.Column('individual', sa.String(100), nullable=True),
        sa.Column('old_address', sa.Text(), nullable=True),
        sa.Column('new_address', sa.Text(), nullable=True),
        sa.Column('distance_from_old_to_new', sa.String(50), nullable=True),
        sa.Column('distance_from_new_to_office', sa.String(50), nullable=True),
        sa.Column('air_ticket_cost', sa.Float(), server_default='0.0'),
        sa.Column('movers_and_packers', sa.Float(), server_default='0.0'),
        sa.Column('meals_and_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('any_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('date_of_travel', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_of_joining', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('new_employer_address', sa.Text(), nullable=True),
        sa.Column('gross_income_after_moving', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_moving_expenses_individual table
    op.create_table(
        't1_moving_expenses_individual',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False, unique=True),
        sa.Column('individual', sa.String(100), nullable=True),
        sa.Column('old_address', sa.Text(), nullable=True),
        sa.Column('new_address', sa.Text(), nullable=True),
        sa.Column('distance_from_old_to_new', sa.String(50), nullable=True),
        sa.Column('distance_from_new_to_office', sa.String(50), nullable=True),
        sa.Column('air_ticket_cost', sa.Float(), server_default='0.0'),
        sa.Column('movers_and_packers', sa.Float(), server_default='0.0'),
        sa.Column('meals_and_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('any_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('date_of_travel', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_of_joining', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('new_employer_address', sa.Text(), nullable=True),
        sa.Column('gross_income_after_moving', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_moving_expenses_spouse table
    op.create_table(
        't1_moving_expenses_spouse',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False, unique=True),
        sa.Column('individual', sa.String(100), nullable=True),
        sa.Column('old_address', sa.Text(), nullable=True),
        sa.Column('new_address', sa.Text(), nullable=True),
        sa.Column('distance_from_old_to_new', sa.String(50), nullable=True),
        sa.Column('distance_from_new_to_office', sa.String(50), nullable=True),
        sa.Column('air_ticket_cost', sa.Float(), server_default='0.0'),
        sa.Column('movers_and_packers', sa.Float(), server_default='0.0'),
        sa.Column('meals_and_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('any_other_cost', sa.Float(), server_default='0.0'),
        sa.Column('date_of_travel', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_of_joining', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('new_employer_address', sa.Text(), nullable=True),
        sa.Column('gross_income_after_moving', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_self_employment table
    op.create_table(
        't1_self_employment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_id', sa.String(50), nullable=False, unique=True),
        sa.Column('business_types', postgresql.JSON(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['form_id'], ['t1_forms_main.id'], ondelete='CASCADE'),
    )
    
    # Create t1_uber_business table
    op.create_table(
        't1_uber_business',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('self_employment_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('uber_skip_statement', sa.String(200), nullable=True),
        sa.Column('business_hst_number', sa.String(50), nullable=True),
        sa.Column('hst_access_code', sa.String(50), nullable=True),
        sa.Column('hst_filling_period', sa.String(50), nullable=True),
        sa.Column('total_km_for_uber_skip', sa.Float(), server_default='0.0'),
        sa.Column('total_official_km_driven', sa.Float(), server_default='0.0'),
        sa.Column('total_km_driven_entire_year', sa.Float(), server_default='0.0'),
        sa.Column('business_number_vehicle_registration', sa.Float(), server_default='0.0'),
        sa.Column('meals', sa.Float(), server_default='0.0'),
        sa.Column('telephone', sa.Float(), server_default='0.0'),
        sa.Column('parking_fees', sa.Float(), server_default='0.0'),
        sa.Column('cleaning_expenses', sa.Float(), server_default='0.0'),
        sa.Column('safety_inspection', sa.Float(), server_default='0.0'),
        sa.Column('winter_tire_change', sa.Float(), server_default='0.0'),
        sa.Column('oil_change_and_maintenance', sa.Float(), server_default='0.0'),
        sa.Column('depreciation', sa.Float(), server_default='0.0'),
        sa.Column('insurance_on_vehicle', sa.Float(), server_default='0.0'),
        sa.Column('gas', sa.Float(), server_default='0.0'),
        sa.Column('financing_cost_interest', sa.Float(), server_default='0.0'),
        sa.Column('lease_cost', sa.Float(), server_default='0.0'),
        sa.Column('other_expense1', sa.Float(), server_default='0.0'),
        sa.Column('other_expense2', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['self_employment_id'], ['t1_self_employment.id'], ondelete='CASCADE'),
    )
    
    # Create t1_general_business table (simplified - full table has many columns)
    op.create_table(
        't1_general_business',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('self_employment_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('client_name', sa.String(200), nullable=True),
        sa.Column('business_name', sa.String(200), nullable=True),
        sa.Column('sales_commissions_fees', sa.Float(), server_default='0.0'),
        sa.Column('minus_hst_collected', sa.Float(), server_default='0.0'),
        sa.Column('gross_income', sa.Float(), server_default='0.0'),
        # Add all other columns as needed - this is a simplified version
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['self_employment_id'], ['t1_self_employment.id'], ondelete='CASCADE'),
    )
    
    # Create t1_rental_income table
    op.create_table(
        't1_rental_income',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('self_employment_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('property_address', sa.Text(), nullable=True),
        sa.Column('co_owner_partner1', sa.String(200), nullable=True),
        sa.Column('co_owner_partner2', sa.String(200), nullable=True),
        sa.Column('co_owner_partner3', sa.String(200), nullable=True),
        sa.Column('number_of_units', sa.Integer(), server_default='0'),
        sa.Column('gross_rental_income', sa.Float(), server_default='0.0'),
        sa.Column('any_govt_income_relating_to_rental', sa.Float(), server_default='0.0'),
        sa.Column('personal_use_portion', sa.String(50), nullable=True),
        sa.Column('house_insurance', sa.Float(), server_default='0.0'),
        sa.Column('mortgage_interest', sa.Float(), server_default='0.0'),
        sa.Column('property_taxes', sa.Float(), server_default='0.0'),
        sa.Column('utilities', sa.Float(), server_default='0.0'),
        sa.Column('management_admin_fees', sa.Float(), server_default='0.0'),
        sa.Column('repair_and_maintenance', sa.Float(), server_default='0.0'),
        sa.Column('cleaning_expense', sa.Float(), server_default='0.0'),
        sa.Column('motor_vehicle_expenses', sa.Float(), server_default='0.0'),
        sa.Column('legal_professional_fees', sa.Float(), server_default='0.0'),
        sa.Column('advertising_promotion', sa.Float(), server_default='0.0'),
        sa.Column('other_expense', sa.Float(), server_default='0.0'),
        sa.Column('purchase_price', sa.Float(), server_default='0.0'),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('addition_deletion_amount', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['self_employment_id'], ['t1_self_employment.id'], ondelete='CASCADE'),
    )


def downgrade():
    op.drop_table('t1_rental_income')
    op.drop_table('t1_general_business')
    op.drop_table('t1_uber_business')
    op.drop_table('t1_self_employment')
    op.drop_table('t1_moving_expenses_spouse')
    op.drop_table('t1_moving_expenses_individual')
    op.drop_table('t1_moving_expenses')
    op.drop_table('t1_foreign_properties')
    op.drop_table('t1_child_info')
    op.drop_table('t1_spouse_info')
    op.drop_table('t1_personal_info')
    op.drop_table('t1_forms_main')















