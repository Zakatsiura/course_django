from django.views.generic import TemplateView
from hr.models import Company 

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['company_logo'] = company.logo.url if company and company.logo else None
        return context

