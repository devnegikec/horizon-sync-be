from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.utils.exceptions import HorizonException

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(HorizonException)
    async def horizon_exception_handler(request: Request, exc: HorizonException):
        return JSONResponse(
            status_code=exc.to_http_exception().status_code,
            content=exc.to_http_exception().detail
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "code": "VALIDATION_ERROR",
                "details": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # In production, you might want to log this and return a generic error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(exc)
            }
        )
