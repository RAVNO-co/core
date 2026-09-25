class Interactor[InputDTO, OutputDTO]:
    """
    Buisness logic executor
    """

    async def __call__(self, context: InputDTO) -> OutputDTO:
        raise NotImplementedError
