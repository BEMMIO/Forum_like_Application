from django.contrib.sites.models import Site

def get_current_site_for_this_project():
	# func. returns the current site .
	# NB: change this object before using this function as it returns default: example.com
	# ToDo : cache this func.
	site = Site.objects.get_current()
	return site 


def get_next(request):
    """
    1. If there is a variable named ``next`` in the *POST* parameters, the
    view will redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the 
    view will redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the 
    view will redirect to that previous page.
    
    """
    return request.POST.get('next', request.GET.get('next', 
        request.META.get('HTTP_REFERER', None)))