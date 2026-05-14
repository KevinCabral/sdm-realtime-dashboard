from dataclasses import dataclass


@dataclass
class UserContext:
    username: str
    role: str


def authenticate_request() -> UserContext:
    """Authentication placeholder for future SSO/JWT integration."""
    return UserContext(username="demo_user", role="election_operator")


def authorize_access(user: UserContext, required_role: str) -> bool:
    """Role-based access placeholder for future policy engine integration."""
    return user.role == required_role
