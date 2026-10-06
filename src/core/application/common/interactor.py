class Interactor[InputDTO, OutputDTO]:
    """
    Business logic executor
    """

    async def __call__(self, context: InputDTO) -> OutputDTO:
        raise NotImplementedError
