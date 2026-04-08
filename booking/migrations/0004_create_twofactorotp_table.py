# Generated manually to fix missing TwoFactorOTP table

from django.db import migrations, models, connection


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]


def create_model_if_not_exists(apps, schema_editor):
    """Create TwoFactorOTP model only if it doesn't exist"""
    if not check_table_exists('booking_twofactorotp'):
        # Table doesn't exist, create it
        TwoFactorOTP = apps.get_model('booking', 'TwoFactorOTP')
        with schema_editor.connection.cursor() as cursor:
            schema_editor.create_model(TwoFactorOTP)


def reverse_create_model(apps, schema_editor):
    """Reverse operation - delete the table if it exists"""
    if check_table_exists('booking_twofactorotp'):
        TwoFactorOTP = apps.get_model('booking', 'TwoFactorOTP')
        schema_editor.delete_model(TwoFactorOTP)


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_artist_email_artist_password'),
    ]

    operations = [
        migrations.RunPython(
            create_model_if_not_exists,
            reverse_create_model,
        ),
    ]
