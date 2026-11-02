class Role:
    SUPER_ADMIN = "super_admin"
    ADMINISTRATOR = "administrator"
    FINANCE_OFFICER = "finance_officer"
    PASTOR = "pastor"
    SECRETARY = "secretary"
    CELL_LEADER = "cell_leader"
    DATA_ENTRY = "data_entry"

    CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (ADMINISTRATOR, "Administrator"),
        (FINANCE_OFFICER, "Finance Officer"),
        (PASTOR, "Pastor / Overseer"),
        (SECRETARY, "Secretary"),
        (CELL_LEADER, "Cell Leader"),
        (DATA_ENTRY, "Data Entry Clerk"),
    ]

    # Role hierarchy levels (higher = more access)
    LEVELS = {
        SUPER_ADMIN: 7,
        ADMINISTRATOR: 6,
        FINANCE_OFFICER: 5,
        PASTOR: 5,
        SECRETARY: 4,
        CELL_LEADER: 3,
        DATA_ENTRY: 2,
    }

    FINANCE_ROLES = {SUPER_ADMIN, ADMINISTRATOR, FINANCE_OFFICER}
    PASTORAL_ROLES = {SUPER_ADMIN, ADMINISTRATOR, PASTOR}
    ADMIN_ROLES = {SUPER_ADMIN, ADMINISTRATOR}
    ALL_ROLES = {SUPER_ADMIN, ADMINISTRATOR, FINANCE_OFFICER, PASTOR, SECRETARY, CELL_LEADER, DATA_ENTRY}
