# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('participants', models.ManyToManyField(to='chat.ChatUser')),
                ('messages', models.ManyToManyField(to='chat.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
