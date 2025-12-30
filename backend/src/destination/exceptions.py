from fastapi import HTTPException, status

class DestinationNotFoundError(HTTPException):
    def __init__(self, destination_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with id {destination_id} not found"
        )
