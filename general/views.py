from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from hr.models import Company 
        company = Company.objects.first()
        context['company_logo'] = company.logo.url if company and company.logo else None
        return context

