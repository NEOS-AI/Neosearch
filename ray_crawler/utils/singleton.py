class Singleton(type):
    """The singleton metaclass."""

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Override to create only one instance ever.

        Returns:
            object: Instance of the class initialized.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
