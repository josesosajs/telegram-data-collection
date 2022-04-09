import uuid

class User:
    def __init__(self, **kwargs):
        self.internal_id = str(uuid.uuid4())
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

class Channel:
	def __init__(self, **kwargs):
		self.internal_id = str(uuid.uuid4())
		for key in kwargs.keys():
			self.__setattr__(key, kwargs[key])

class Message:
	def __init__(self, **kwargs):
		self.internal_id = str(uuid.uuid4())
		for key in kwargs.keys():
			self.__setattr__(key, kwargs[key])

class Message_media:
	def __init__(self, **kwargs):
		self.internal_id = str(uuid.uuid4())
		for key in kwargs.keys():
			self.__setattr__(key, kwargs[key])
