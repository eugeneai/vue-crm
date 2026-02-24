"""
Модель Contact (Контакты) для личной CRM системы.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Contact(Base):
    """
    Модель контакта.
    
    Атрибуты:
        id: Уникальный идентификатор
        full_name: ФИО контакта (обязательно)
        company: Место работы (опционально)
        phone: Телефон (опционально)
        email: Email (опционально)
    
    Отношения:
        meetings: Список встреч с этим контактом
    """
    
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False, index=True)
    company = Column(String(200), index=True)
    phone = Column(String(50), index=True)
    email = Column(String(100))
    
    # Отношения
    meetings = relationship(
        "Meeting", 
        back_populates="contact", 
        cascade="all, delete-orphan",
        lazy="dynamic"  # Для ленивой загрузки больших списков
    )
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, full_name='{self.full_name}')>"
    
    def __str__(self) -> str:
        return f"{self.full_name}" + (f" ({self.company})" if self.company else "")
    
    def to_dict(self) -> dict:
        """
        Конвертировать контакт в словарь.
        
        Returns:
            Словарь с данными контакта
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email
        }
    
    @classmethod
    def validate(cls, data: dict) -> tuple[bool, list[str]]:
        """
        Валидация данных контакта.
        
        Args:
            data: Словарь с данными для валидации
            
        Returns:
            Кортеж (is_valid, errors)
        """
        errors = []
        
        # Проверка обязательных полей
        if not data.get('full_name'):
            errors.append("Full name is required")
        elif len(data['full_name']) > 200:
            errors.append("Full name must be 200 characters or less")
        
        # Проверка опциональных полей
        if data.get('company') and len(data['company']) > 200:
            errors.append("Company must be 200 characters or less")
        
        if data.get('phone') and len(data['phone']) > 50:
            errors.append("Phone must be 50 characters or less")
        
        if data.get('email'):
            if len(data['email']) > 100:
                errors.append("Email must be 100 characters or less")
            elif '@' not in data['email']:
                errors.append("Email must be a valid email address")
        
        return len(errors) == 0, errors