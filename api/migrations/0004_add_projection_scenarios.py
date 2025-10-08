# Generated manually for projection scenarios

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_financialprofile_current_savings_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectionScenario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('scenario_type', models.CharField(choices=[('conservative', 'Conservative'), ('moderate', 'Moderate'), ('aggressive', 'Aggressive'), ('custom', 'Custom')], default='moderate', max_length=20)),
                ('annual_return_rate', models.DecimalField(decimal_places=2, help_text='Expected annual return percentage', max_digits=5)),
                ('inflation_rate', models.DecimalField(decimal_places=2, help_text='Expected inflation rate percentage', max_digits=5)),
                ('risk_tolerance', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectionYearlyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('beginning_balance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('contributions', models.DecimalField(decimal_places=2, max_digits=12)),
                ('gains', models.DecimalField(decimal_places=2, max_digits=12)),
                ('ending_balance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('inflation_adjusted_balance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('projection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yearly_data', to='api.projectionresult')),
            ],
            options={
                'ordering': ['year'],
            },
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='annual_return_rate',
            field=models.DecimalField(decimal_places=2, max_digits=5, default=7.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='inflation_rate',
            field=models.DecimalField(decimal_places=2, max_digits=5, default=3.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='monthly_contribution',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.projectionscenario'),
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='total_contributions',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='projectionresult',
            name='total_gains',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterUniqueTogether(
            name='projectionyearlydata',
            unique_together={('projection', 'year')},
        ),
    ]

