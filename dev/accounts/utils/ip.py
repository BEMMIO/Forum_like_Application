import socket


def visitor_ip_address(request):
	x_forwarded_for = request.META.get('HTTP_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip



def is_valid_ip_address(ip = None):
	if not ip is None:
		try:
			socket.inet_aton(ip)
			ip_valid = True
		except (AttributeError,socket.error):
			return False
		return ip_valid



def location_of_ip_address(ip = None):
	pass
