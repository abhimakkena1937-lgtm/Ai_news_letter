from database import (
    init_db,
    add_subscriber,
    get_active_subscribers
)


init_db()

add_subscriber("abhimakkena1937@gmail.com")

print(
    get_active_subscribers()
)