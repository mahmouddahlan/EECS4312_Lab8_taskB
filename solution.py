## Student Name: Mahmoud Dahlan
## Student ID: 219673896

"""
Task B: Event Registration with waitlisted (Stub)

Implement an event registration module with:
  - fixed capacity
  - FIFO waitlisted
  - promotion on cancellation (earliest waitlisted user)
  - duplicate prevention
  - status queries
See the lab handout for full requirements.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlisted position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Students must implement this class per the lab handout.
    Deterministic ordering is required (e.g., FIFO waitlisted, predictable registration order).
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        # TODO: Initialize internal data structures
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self._capacity: int = capacity
        self._registered: List[str] = []
        self._waitlisted: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        # TODO: Implement per lab handout
        if user_id in self._registered or user_id in self._waitlisted:
            raise DuplicateRequest(f"{user_id} is already in the system")

        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            return UserStatus(state="registered", position=None)

        # capacity full (including when capacity == 0)
        self._waitlisted.append(user_id)
        return UserStatus(state="waitlisted", position=len(self._waitlisted))
    
    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlisted
          - behavior when user not found depends on handout (raise NotFound or ignore)

        Raises:
            NotFound (if required by handout)
        """
        # TODO: Implement per lab handout
        if user_id in self._registered:
            self._registered.remove(user_id)
            # promote if possible
            if self._waitlisted and len(self._registered) < self._capacity:
                promoted = self._waitlisted.pop(0)
                self._registered.append(promoted)
            return

        if user_id in self._waitlisted:
            self._waitlisted.remove(user_id)
            return
        
        raise NotFound(f"{user_id} not found")
        # not found: no-op by assumption
        # If your handout requires raising, replace with:
        # raise NotFound(f"{user_id} not found")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        # TODO: Implement per lab handout
        if user_id in self._registered:
            return UserStatus(state="registered", position=None)
        if user_id in self._waitlisted:
            pos = self._waitlisted.index(user_id) + 1
            return UserStatus(state="waitlisted", position=pos)
        return UserStatus(state="none", position=None)
    
    def snapshot(self) -> dict:
        """
        (Optional helper for debugging/tests)
        Return a deterministic snapshot of internal state.
        """
        # TODO: Implement if required/allowed
        return {
        "registered": list(self._registered),
        "waitlist": list(self._waitlisted),
        "capacity": self._capacity
        }