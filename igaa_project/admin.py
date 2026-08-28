from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static

# Professional Admin Customization
admin.site.site_header = "GIA Hajj Operations"
admin.site.site_title = "GIA Administration"
admin.site.index_title = "Dashboard"

# Custom Admin Site Styling
class ProfessionalAdminSite(admin.AdminSite):
    site_header = "GIA Hajj Operations Management"
    site_title = "GIA Admin"
    index_title = "Welcome to Administration"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['site_header'] = self.site_header
        return super().index(request, extra_context)

# Apply professional styling to default admin site
admin.site.site_header = format_html(
    '<span style="color: white; font-weight: bold; font-size: 20px;">GIA Hajj Operations</span>'
)
admin.site.site_title = "GIA Admin"
admin.site.index_title = "Administration Dashboard"

# Inject CSS
original_admin_css = admin.site.each_context

def each_context(request):
    context = original_admin_css(request) if callable(original_admin_css) else original_admin_css
    context['extra_css'] = [
        static('admin/css/professional-admin.css')
    ]
    return context

admin.site.each_context = each_context
