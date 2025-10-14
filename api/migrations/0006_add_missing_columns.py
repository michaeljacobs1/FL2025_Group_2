# Generated manually to add missing columns

# from django.db import migrations, models
# import django.db.models.deletion


# class Migration(migrations.Migration):

#     dependencies = [
#         ('api', '0005_merge_20251008_1450'),
#     ]

#     operations = [
#         migrations.AddField(
#             model_name='projectionresult',
#             name='scenario_id',
#             field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.projectionscenario'),
#         ),
#         migrations.AddField(
#             model_name='projectionresult',
#             name='annual_return_rate',
#             field=models.DecimalField(decimal_places=2, max_digits=5, default=7.0),
#         ),
#         migrations.AddField(
#             model_name='projectionresult',
#             name='inflation_rate',
#             field=models.DecimalField(decimal_places=2, max_digits=5, default=3.0),
#         ),
#         migrations.AddField(
#             model_name='projectionresult',
#             name='monthly_contribution',
#             field=models.DecimalField(decimal_places=2, max_digits=12, default=0),
#         ),
#         migrations.AddField(
#             model_name='projectionresult',
#             name='total_contributions',
#             field=models.DecimalField(decimal_places=2, max_digits=12, default=0),
#         ),
#         migrations.AddField(
#             model_name='projectionresult',
#             name='total_gains',
#             field=models.DecimalField(decimal_places=2, max_digits=12, default=0),
#         ),
#     ]

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('api', '0005_merge_20251008_1450')]
    operations = []
