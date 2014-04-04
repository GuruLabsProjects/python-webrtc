# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.CharField(primary_key=True, default='Message:messageIdGenerator', serialize=False, editable=False, max_length=36, unique=True)),
                ('text', models.CharField(max_length=256, editable=False)),
                ('timestamp', models.DateTimeField(verbose_name='date submitted')),
                ('sender', models.ForeignKey(to='chat.ChatUser', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
