import os

import markdown
from django.shortcuts import render
from django.http import HttpResponse

from src.os_calls.basic_os_calls import get_root_path


def api_documentation_view(request):
    """
    provide a web view for the API documentation
    Args:
        request: django Request object

    Returns: html Render

    """
    cpath = get_root_path()
    api_documentation_path = os.path.join(cpath, "docs", "API_DOCUMENTATION.md")
    with open(api_documentation_path, 'r') as file:
        content = file.read()
        html_content = markdown.markdown(content, extensions=['fenced_code'])
    return render(request, 'api_documentation.html', {'content': html_content})


def raw_markdown_view(request):
    """
    provide a raw markdown view of the API documentation
    Args:
        request: django Request object

    Returns: html Render

    """
    with open('../docs/API_DOCUMENTATION.md', 'r') as file:
        content = file.read()
    return HttpResponse(content, content_type='text/plain')