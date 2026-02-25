checkdirs := src

style:
	black $(checkdirs)
	isort $(checkdirs)
