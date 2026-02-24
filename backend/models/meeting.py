"""
Модель Meeting (Встречи) для личной CRM системы.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class Meeting(Base):
    """
    Модель встречи.
    
    Атрибуты:
        id: Уникальный идентификатор
        contact_id: ID связанного контакта (обязательно)
        date_time: Дата и время встречи (обязательно)
        topic: Тема встречи (обязательно)
        location: Место встречи (опционально)
    
    Отношения:
        contact: Контакт, с которым происходит встреча
        notes: Список заметок по этой встрече
    """
    
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False, index=True)
    date_time = Column(DateTime, nullable=False, index=True)
    topic = Column(String(500), nullable=False, index=True)
    location = Column(String(200))
    
    # Отношения
    contact = relationship("Contact", back_populates="meetings")
    notes = relationship(
        "Note", 
        back_populates="meeting", 
        cascade="all, delete-orphan",
        lazy="dynamic"  # Для ленивой загрузки больших списков
    )
    
    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, topic='{self.topic}', date_time={self.date_time})>"
    
    def __str__(self) -> str:
        date_str = self.date_time.strftime('%Y-%m-%d %H:%M')
        return f"{date_str}: {self.topic}" + (f" @ {self.location}" if self.location else "")
    
    def to_dict(self, include_contact: bool = False, include_notes: bool = False) -> dict:
        """
        Конвертировать встречу в словарь.
        
        Args:
            include_contact: Включать ли данные контакта
            include_notes: Включать ли список заметок
            
        Returns:
            Словарь с данными встречи
        """
        result = {
            'id': self.id,
            'contact_id': self.contact_id,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'topic': self.topic,
            'location': self.location
        }
        
        if include_contact and self.contact:
            result['contact'] = self.contact.to_dict()
        
        if include_notes:
            result['notes'] = [note.to_dict() for note in self.notes]
        
        return result
    
    @classmethod
    def validate(cls, data: dict) -> tuple[bool, list[str]]:
        """
        Валидация данных встречи.
        
        Args:
            data: Словарь с данными для валидации
            
        Returns:
            Кортеж (is_valid, errors)
        """
        errors = []
        
        # Проверка обязательных полей
        if not data.get('contact_id'):
            errors.append("Contact ID is required")
        
        if not data.get('date_time'):
            errors.append("Date and time is required")
        else:
            try:
                # Пытаемся преобразовать в datetime
                if isinstance(data['date_time'], str):
                    dt = datetime.fromisoformat(data['date_time'].replace('Z', '+00:00'))
                else:
                    dt = data['date_time']
                
                # Проверяем, что дата не в прошлом (для создания новых встреч)
                if 'id' not in data and dt < datetime.now():
                    errors.append("Meeting date cannot be in the past")
            except (ValueError, TypeError):
                errors.append("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        if not data.get('topic'):
            errors.append("Topic is required")
        elif len(data['topic']) > 500:
            errors.append("Topic must be 500 characters or less")
        
        # Проверка опциональных полей
        if data.get('location') and len(data['location']) > 200:
            errors.append("Location must be 200 characters or less")
        
        return len(errors) == 0, errors
    
    def is_upcoming(self, days: int = 7) -> bool:
        """
        Проверить, является ли встреча предстоящей в указанный период.
        
        Args:
            days: Количество дней для проверки (по умолчанию 7)
            
        Returns:
            True если встреча в ближайшие `days` дней
        """
        if not self.date_time:
            return False
        
        now = datetime.now()
        future_limit = now.replace(hour=23, minute=59, second=59) + timedelta(days=days)
        
        return now <= self.date_time <= future_limit