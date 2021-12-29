class InvitationDoesNotExists(Exception):

	def __init__(self,mssg=None):
		if mssg is None:
			mssg = "invitation does not exists."
		super().__init__(mssg)


class InvalidInviationCode(Exception):

	def __init__(self,mssg=None):
		if mssg is None:
			mssg = "invalid invitation code."
		super().__init__(mssg)