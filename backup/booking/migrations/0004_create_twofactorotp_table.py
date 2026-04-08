# Generated manually to fix missing TwoFactorOTP table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_artist_email_artist_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwoFactorOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(max_length=254)),
                ('otp', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('login_method', models.CharField(choices=[('email', 'Email Login'), ('google', 'Google OAuth'), ('artist_email', 'Artist Email Login')], max_length=20)),
                ('user_type', models.CharField(choices=[('client', 'Client'), ('artist', 'Artist')], default='client', max_length=10)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
