"""Calendar integration for appointment booking"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CalendarProvider(ABC):
    """Abstract base class for calendar providers"""

    @abstractmethod
    async def check_availability(
        self, date: datetime, duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Check availability for a date"""
        pass

    @abstractmethod
    async def book_appointment(
        self, contact_name: str, contact_email: str, start_time: datetime,
        duration_minutes: int, title: str
    ) -> Dict[str, Any]:
        """Book an appointment"""
        pass


class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar integration"""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Google Calendar provider"""
        self.credentials_path = credentials_path
        self.service = None
        logger.info("Initialized Google Calendar provider")

    async def check_availability(
        self, date: datetime, duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Check availability for a date"""
        # This is a mock implementation for the POC
        # In production, use Google Calendar API to check real availability
        logger.info(
            "Checking Google Calendar availability",
            date=date.isoformat(),
            duration=duration_minutes,
        )

        available_slots = [
            {
                "start": datetime(date.year, date.month, date.day, 9, 0),
                "end": datetime(date.year, date.month, date.day, 9, 30),
            },
            {
                "start": datetime(date.year, date.month, date.day, 10, 0),
                "end": datetime(date.year, date.month, date.day, 10, 30),
            },
            {
                "start": datetime(date.year, date.month, date.day, 14, 0),
                "end": datetime(date.year, date.month, date.day, 14, 30),
            },
        ]

        return available_slots

    async def book_appointment(
        self,
        contact_name: str,
        contact_email: str,
        start_time: datetime,
        duration_minutes: int,
        title: str,
    ) -> Dict[str, Any]:
        """Book an appointment on Google Calendar"""
        logger.info(
            "Booking Google Calendar appointment",
            contact=contact_name,
            start_time=start_time.isoformat(),
        )

        appointment = {
            "id": f"goog_{start_time.timestamp()}",
            "title": title,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "start_time": start_time.isoformat(),
            "duration_minutes": duration_minutes,
            "provider": "google",
            "status": "booked",
        }

        return appointment


class MockCalendarProvider(CalendarProvider):
    """Mock calendar provider for testing"""

    def __init__(self):
        """Initialize mock calendar provider"""
        logger.info("Initialized Mock Calendar provider")

    async def check_availability(
        self, date: datetime, duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Return mock availability slots"""
        logger.info("Mock: Checking availability", date=date.isoformat())

        from datetime import timedelta

        slots = []
        for hour in [9, 10, 11, 14, 15]:
            start = datetime(date.year, date.month, date.day, hour, 0)
            end = start + timedelta(minutes=duration_minutes)
            slots.append({"start": start, "end": end})

        return slots

    async def book_appointment(
        self,
        contact_name: str,
        contact_email: str,
        start_time: datetime,
        duration_minutes: int,
        title: str,
    ) -> Dict[str, Any]:
        """Book a mock appointment"""
        logger.info(
            "Mock: Booking appointment",
            contact=contact_name,
            start_time=start_time.isoformat(),
        )

        appointment = {
            "id": f"mock_{int(start_time.timestamp())}",
            "title": title,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "start_time": start_time.isoformat(),
            "duration_minutes": duration_minutes,
            "provider": "mock",
            "status": "booked",
        }

        return appointment


class CalendarFactory:
    """Factory for creating calendar provider instances"""

    @staticmethod
    def create(provider_type: str = "mock", **kwargs) -> CalendarProvider:
        """Create a calendar provider instance"""
        if provider_type == "google":
            return GoogleCalendarProvider(**kwargs)
        elif provider_type == "mock":
            return MockCalendarProvider()
        else:
            return MockCalendarProvider()
