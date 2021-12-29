from django.core.exceptions import ValidationError

IMAGE_FILE_VALIDATION_EXTENSIONS = ['png','jpeg','jpg']


def validate_uploaded_file(uploaded):
	try:
		validate_file_size(uploaded)
		validate_file_extension(uploaded)
	except ValidationError as e:
		return e
	return True


def validate_file_size(upload):
	limit = 1024 * 1024 * 1 # 1 MB
	if upload.size > limit:
		raise ValidationError('upload file size must not exceed 1 MB')
	return True


def validate_file_extension(upload):

	def get_extension_type():
	return {
	'image':IMAGE_FILE_VALIDATION_EXTENSIONS
	}

	file_name = upload.name
	file_extension = file_name.lower().split('.')[-1]
	if file_extension not in get_extension_type()['image']:
		message = '{0} extension not allowed,allowed extensions ({1})'
		display_extensions = "."+",".join(get_extension_type()['image'])
		raise ValidationError(message.format(file_extension,display_extensions))
	return True
