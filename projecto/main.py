#main
from auth import login_user

usuario_id = login_user(
    "ruby",
    "123456"
)

print("ID", usuario_id)
