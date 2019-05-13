# Generated by Django 2.1.7 on 2019-05-08 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_user_register_complete'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=200, null=True)),
                ('mimetype', models.CharField(max_length=200)),
                ('text_attachment', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OutboundEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('FAILED', 'Failed'), ('SENT', 'Sent'), ('PENDING', 'Pending'), ('NOT_SENT', 'Not Sent')], default='PENDING', max_length=20)),
                ('last_requested_date', models.DateTimeField(auto_now_add=True)),
                ('format', models.CharField(default='Email', max_length=20)),
                ('to_name', models.CharField(max_length=170, null=True)),
                ('to_email', models.CharField(max_length=254)),
                ('subject', models.CharField(max_length=4000, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='emailattachment',
            name='mail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='web.OutboundEmail'),
        ),
    ]