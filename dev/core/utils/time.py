import humanize


def better_readable_datetime(datetime_obj):

	timelapse = datetime_obj.replace(tzinfo=None)

	return humanize.naturaltime(timelapse)