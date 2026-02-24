"""
Модель Note (Заметки) для личной CRM системы.
"""

from datetime import date
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class Note(Base):
    """
    Модель заметки.
    
    Атрибуты:
        id: Уникальный идентификатор
        meeting_id: ID связанной встречи (обязательно)
        date: Дата заметки (обязательно)
        text: Текст заметки (обязательно)
    
    Отношения:
        meeting: Встреча, к которой относится заметка
    """
    
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    text = Column(Text, nullable=False)
    
    # Отношения
    meeting = relationship("Meeting", back_populates="notes")
    
    def __repr__(self) -> str:
        text_preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"<Note(id={self.id}, date={self.date}, text='{text_preview}')>"
    
    def __str__(self) -> str:
        date_str = self.date.strftime('%Y-%m-%d')
        text_preview = self.text[:100] + '...' if len(self.text) > 100 else self.text
        return f"{date_str}: {text_preview}"
    
    def to_dict(self, include_meeting: bool = False) -> dict:
        """
        Конвертировать заметку в словарь.
        
        Args:
            include_meeting: Включать ли данные встречи
            
        Returns:
            Словарь с данными заметки
        """
        result = {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'date': self.date.isoformat() if self.date else None,
            'text': self.text
        }
        
        if include_meeting and self.meeting:
            result['meeting'] = self.meeting.to_dict(include_contact=True)
        
        return result
    
    @classmethod
    def validate(cls, data: dict) -> tuple[bool, list[str]]:
        """
        Валидация данных заметки.
        
        Args:
            data: Словарь с данными для валидации
            
        Returns:
            Кортеж (is_valid, errors)
        """
        errors = []
        
        # Проверка обязательных полей
        if not data.get('meeting_id'):
            errors.append("Meeting ID is required")
        
        if not data.get('date'):
            errors.append("Date is required")
        else:
            try:
                # Пытаемся преобразовать в date
                if isinstance(data['date'], str):
                    d = date.fromisoformat(data['date'])
                else:
                    d = data['date']
                
                # Проверяем, что дата не в будущем
                if d > date.today():
                    errors.append("Note date cannot be in the future")
            except (ValueError, TypeError):
                errors.append("Invalid date format. Use ISO format (YYYY-MM-DD)")
        
        if not data.get('text'):
            errors.append("Text is required")
        elif not data['text'].strip():
            errors.append("Text cannot be empty or whitespace only")
        
        return len(errors) == 0, errors
    
    def get_preview(self, max_length: int = 100) -> str:
        """
        Получить превью текста заметки.
        
        Args:
            max_length: Максимальная длина превью
            
        Returns:
            Превью текста
        """
        if len(self.text) <= max_length:
            return self.text
        
        # Обрезаем до последнего пробела перед max_length
        preview = self.text[:max_length]
        last_space = preview.rfind(' ')
        
        if last_space > max_length * 0.7:  # Если есть разумное место для обрезки
            preview = preview[:last_space]
        
        return preview + '...'