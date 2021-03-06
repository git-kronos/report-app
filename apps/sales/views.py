from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Sale
from apps.sales.forms import SaleSearchForm
from apps.sales.utils import get_customer_from_id, get_salesman_from_id, get_chart
import pandas as pd
from apps.reports.forms import ReportForm


# Create your views here.
def home_view(request):
    chart = df = sales_df = positions_df = merged_df = None

    search_form = SaleSearchForm(request.POST or None)
    report_form = ReportForm()
    if request.method == 'POST':
        date_form = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        chart_type = request.POST.get('chart_type')
        results_by = request.POST.get('results_by')

        sale_qs = Sale.objects.filter(
            created__date__lte=date_to, created__date__gte=date_form)
        if len(sale_qs) > 0:
            sales_df = pd.DataFrame(sale_qs.values())
            sales_df['customer_id'] = sales_df['customer_id'].apply(
                get_customer_from_id)
            sales_df['salesman_id'] = sales_df['salesman_id'].apply(
                get_salesman_from_id)
            sales_df['created'] = sales_df['created'].apply(
                lambda x: x.strftime('%Y-%m-%d'))
            sales_df['updated'] = sales_df['updated'].apply(
                lambda x: x.strftime('%Y-%m-%d'))

            sales_df.rename({'customer_id': 'customer', 'salesman_id': 'salesman',
                             'id': 'sales_id'}, axis=1, inplace=True)

            positions_data = []
            for sale in sale_qs:
                for pos in sale.get_positions():
                    obj = {
                        'production_id': pos.id,
                        'product': pos.product.name,
                        'quantity': pos.quantity,
                        'price': pos.price,
                        'sales_id': pos.get_sale_id(),
                    }
                    positions_data.append(obj)

            positions_df = pd.DataFrame(positions_data)
            merged_df = pd.merge(sales_df, positions_df, on='sales_id')

            df = merged_df.groupby('transaction_id', as_index=False)['price'].agg('sum')

            chart = get_chart(chart_type, df, labels=df['transaction_id'].values)

            sales_df = sales_df.to_html()
            positions_df = positions_df.to_html()
            merged_df = merged_df.to_html()
            df = df.to_html()

        else:
            print('no data')
    context = {
        'search_form': search_form,
        'report_form': report_form,
        'sales_df': sales_df,
        'positions_df': positions_df,
        'merged_df': merged_df,
        'df': df,
        'chart': chart
    }
    return render(request, 'sales/home.html', context)


class SaleListView(ListView):
    model = Sale
    template_name = 'sales/main.html'
    # context_object_name = 'sales'


class SaleDetailView(DetailView):
    model = Sale
    template_name = 'sales/detail.html'
    # context_object_name = 'sales'
