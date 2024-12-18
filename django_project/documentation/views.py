from django.shortcuts import render
import markdown
from django.shortcuts import render
from django.http import HttpResponse

def api_documentation_view(request):
    with open('../docs/API_DOCUMENTATION.md', 'r') as file:
        content = file.read()
        html_content = markdown.markdown(content, extensions=['fenced_code'])
    return render(request, 'api_documentation.html', {'content': html_content})



def raw_markdown_view(request):
    with open('../docs/API_DOCUMENTATION.md', 'r') as file:
        content = file.read()
    return HttpResponse(content, content_type='text/plain')