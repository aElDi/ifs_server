# from fastapi import Depends, Header, HTTPException
# from .config import ND_SERVER_TOKEN
# from typing_extensions import Annotated

# def verifyServer(x_token: Annotated[str, Header()]):
#     if x_token != ND_SERVER_TOKEN:
#         raise HTTPException(404, detail="Not Found")
#     return x_token

# verifyServerDep = Depends(verifyServer)