from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class User:
    user_id: int
    coins: int = 100
    diamonds: int = 0
    skin: str = "👨‍🌾 Фермер"
    planted_crop: Optional[str] = None
    planted_at: Optional[int] = None
    level: int = 1
    exp: int = 0
    last_daily: Optional[int] = None
    daily_streak: int = 0
    nickname: str = ""
    avatar: str = "👨‍🌾"
    achievements: List[str] = None
    total_harvests: int = 0
    total_crops_planted: int = 0
    current_field: int = 1
    last_animal_collect: int = 0
    active_event: Optional[str] = None
    event_end_time: int = 0
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
        if not self.nickname:
            self.nickname = f"Фермер_{self.user_id}"

@dataclass
class Crop:
    name: str
    seed_price: int
    harvest_price: int
    grow_seconds: int
    emoji: str = "🌾"
    exp: int = 10

@dataclass
class Animal:
    name: str
    price: int
    income: int
    interval: int
    emoji: str
    max_count: int

@dataclass
class Upgrade:
    name: str
    price: int
    max_level: int
    effect: str