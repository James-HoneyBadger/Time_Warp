"""
Gamification System for TimeWarp IDE
Adds achievements, badges, challenges, and progress tracking to make learning fun
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class AchievementType(Enum):
    """Types of achievements"""
    FIRST_STEPS = "first_steps"
    CODING_STREAK = "coding_streak" 
    TUTORIAL_MASTER = "tutorial_master"
    BUG_HUNTER = "bug_hunter"
    CODE_ARTIST = "code_artist"
    SPEED_CODER = "speed_coder"
    PROBLEM_SOLVER = "problem_solver"
    MENTOR = "mentor"


class BadgeRarity(Enum):
    """Rarity levels for badges"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Represents an achievement/badge"""
    achievement_id: str
    name: str
    description: str
    icon: str  # Unicode emoji or icon identifier
    rarity: BadgeRarity
    points: int
    requirements: Dict[str, Any]
    unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0


@dataclass
class Challenge:
    """Represents a coding challenge"""
    challenge_id: str
    title: str
    description: str
    language: str
    difficulty: str  # "easy", "medium", "hard"
    category: str    # "logic", "math", "graphics", "algorithms"
    starter_code: str
    solution_template: str
    test_cases: List[Dict[str, Any]]
    points: int
    time_limit: Optional[int] = None  # seconds
    completed: bool = False
    best_time: Optional[float] = None
    attempts: int = 0


@dataclass
class UserStats:
    """User statistics and progress"""
    total_points: int = 0
    level: int = 1
    experience: int = 0
    lines_of_code: int = 0
    programs_written: int = 0
    challenges_completed: int = 0
    tutorials_finished: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity: Optional[str] = None
    languages_used: Optional[Dict[str, int]] = None
    
    def __post_init__(self):
        if self.languages_used is None:
            self.languages_used = {}


class GamificationSystem:
    """Main gamification system for TimeWarp IDE"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.user_stats = UserStats()
        self.data_file = Path.home() / ".timewarp" / "gamification.json"
        
        self.initialize_achievements()
        self.initialize_challenges()
        self.load_data()
        
        # Callbacks for UI updates
        self.achievement_callback: Optional[Any] = None
        self.level_up_callback: Optional[Any] = None
        self.stats_update_callback: Optional[Any] = None

    def set_callbacks(self, achievement_cb: Optional[Any] = None, 
                     level_up_cb: Optional[Any] = None, stats_cb: Optional[Any] = None):
        """Set callback functions for UI updates"""
        self.achievement_callback = achievement_cb
        self.level_up_callback = level_up_cb
        self.stats_update_callback = stats_cb

    def initialize_achievements(self):
        """Initialize all available achievements"""
        
        # First Steps Achievements
        self.achievements["hello_world"] = Achievement(
            achievement_id="hello_world",
            name="Hello, World!",
            description="Write your first program",
            icon="👋",
            rarity=BadgeRarity.COMMON,
            points=10,
            requirements={"programs_written": 1}
        )
        
        self.achievements["first_variable"] = Achievement(
            achievement_id="first_variable", 
            name="Variable Explorer",
            description="Use your first variable",
            icon="📦",
            rarity=BadgeRarity.COMMON,
            points=15,
            requirements={"used_variables": 1}
        )
        
        # Tutorial Achievements
        self.achievements["tutorial_beginner"] = Achievement(
            achievement_id="tutorial_beginner",
            name="Student",
            description="Complete your first tutorial",
            icon="📚",
            rarity=BadgeRarity.COMMON,
            points=25,
            requirements={"tutorials_completed": 1}
        )
        
        self.achievements["tutorial_master"] = Achievement(
            achievement_id="tutorial_master",
            name="Tutorial Master",
            description="Complete all beginner tutorials",
            icon="🎓",
            rarity=BadgeRarity.RARE,
            points=100,
            requirements={"beginner_tutorials_completed": 5}
        )
        
        # Coding Streak Achievements
        self.achievements["streak_3"] = Achievement(
            achievement_id="streak_3",
            name="Getting Started",
            description="Code for 3 days in a row",
            icon="🔥",
            rarity=BadgeRarity.UNCOMMON,
            points=30,
            requirements={"streak_days": 3}
        )
        
        self.achievements["streak_7"] = Achievement(
            achievement_id="streak_7",
            name="Week Warrior",
            description="Code for 7 days straight",
            icon="⚡",
            rarity=BadgeRarity.RARE,
            points=75,
            requirements={"streak_days": 7}
        )
        
        self.achievements["streak_30"] = Achievement(
            achievement_id="streak_30",
            name="Dedication Master",
            description="Code for 30 days in a row",
            icon="💎",
            rarity=BadgeRarity.LEGENDARY,
            points=300,
            requirements={"streak_days": 30}
        )
        
        # Language Mastery
        self.achievements["pilot_master"] = Achievement(
            achievement_id="pilot_master",
            name="PILOT Master",
            description="Write 50 PILOT programs",
            icon="✈️",
            rarity=BadgeRarity.EPIC,
            points=150,
            requirements={"pilot_programs": 50}
        )
        
        self.achievements["polyglot"] = Achievement(
            achievement_id="polyglot",
            name="Polyglot Programmer", 
            description="Write programs in 4 different languages",
            icon="🌍",
            rarity=BadgeRarity.EPIC,
            points=200,
            requirements={"languages_used": 4}
        )
        
        # Graphics and Creativity
        self.achievements["turtle_artist"] = Achievement(
            achievement_id="turtle_artist",
            name="Turtle Artist",
            description="Create 10 turtle graphics programs",
            icon="🎨",
            rarity=BadgeRarity.RARE,
            points=120,
            requirements={"turtle_programs": 10}
        )
        
        # Speed and Efficiency
        self.achievements["speed_demon"] = Achievement(
            achievement_id="speed_demon",
            name="Speed Demon",
            description="Complete a challenge in under 2 minutes",
            icon="💨",
            rarity=BadgeRarity.RARE,
            points=100,
            requirements={"fast_challenge_completion": 120}  # seconds
        )
        
        # Code Quality
        self.achievements["clean_coder"] = Achievement(
            achievement_id="clean_coder",
            name="Clean Coder",
            description="Write 10 programs with no syntax errors",
            icon="✨",
            rarity=BadgeRarity.UNCOMMON,
            points=80,
            requirements={"error_free_programs": 10}
        )

    def initialize_challenges(self):
        """Initialize coding challenges"""
        
        # PILOT Challenges
        self.challenges["pilot_calculator"] = Challenge(
            challenge_id="pilot_calculator",
            title="Simple Calculator",
            description="Create a PILOT program that adds two numbers",
            language="pilot",
            difficulty="easy",
            category="math",
            starter_code="U:A=10\nU:B=5\n# Add your calculation here\nEND",
            solution_template="U:A=10\nU:B=5\nC:RESULT=*A*+*B*\nT:*A* + *B* = *RESULT*\nEND",
            test_cases=[
                {"input": "", "expected_output": "10 + 5 = 15"}
            ],
            points=25
        )
        
        self.challenges["pilot_greeting"] = Challenge(
            challenge_id="pilot_greeting",
            title="Personal Greeting",
            description="Ask for user's name and greet them personally",
            language="pilot",
            difficulty="easy", 
            category="logic",
            starter_code="# Ask for name and create greeting\nEND",
            solution_template="A:What is your name?\nU:NAME=*\nT:Hello, *NAME*! Welcome to PILOT!\nEND",
            test_cases=[
                {"input": "Alice", "expected_output": "Hello, Alice! Welcome to PILOT!"}
            ],
            points=30
        )
        
        # Logo Challenges
        self.challenges["logo_square"] = Challenge(
            challenge_id="logo_square",
            title="Perfect Square",
            description="Draw a square with 100-pixel sides",
            language="logo",
            difficulty="easy",
            category="graphics", 
            starter_code="# Draw a square here",
            solution_template="REPEAT 4 [FORWARD 100 RIGHT 90]",
            test_cases=[
                {"input": "", "expected_output": "[Square drawn]"}
            ],
            points=20
        )
        
        self.challenges["logo_star"] = Challenge(
            challenge_id="logo_star",
            title="Five-Pointed Star",
            description="Draw a perfect five-pointed star",
            language="logo",
            difficulty="medium",
            category="graphics",
            starter_code="# Draw a five-pointed star",
            solution_template="REPEAT 5 [FORWARD 100 RIGHT 144]",
            test_cases=[
                {"input": "", "expected_output": "[Star drawn]"}
            ],
            points=50
        )
        
        # BASIC Challenges
        self.challenges["basic_countdown"] = Challenge(
            challenge_id="basic_countdown",
            title="Countdown Timer",
            description="Create a countdown from 10 to 1",
            language="basic",
            difficulty="medium",
            category="logic",
            starter_code="10 REM Countdown program\n20 REM Add your code here\n30 END",
            solution_template="10 FOR I = 10 TO 1 STEP -1\n20 PRINT I\n30 NEXT I\n40 PRINT \"Blast off!\"\n50 END",
            test_cases=[
                {"input": "", "expected_output": "10\n9\n8\n7\n6\n5\n4\n3\n2\n1\nBlast off!"}
            ],
            points=40
        )
        
        # Code Golf Challenges (shortest code wins)
        self.challenges["golf_hello"] = Challenge(
            challenge_id="golf_hello",
            title="Code Golf: Hello World",
            description="Write the shortest 'Hello World' program possible",
            language="pilot",
            difficulty="easy",
            category="golf",
            starter_code="# Write the shortest Hello World program",
            solution_template="T:Hello World\nEND",
            test_cases=[
                {"input": "", "expected_output": "Hello World"}
            ],
            points=35,
            time_limit=300  # 5 minutes
        )

    def record_activity(self, activity_type: str, data: Optional[Dict[str, Any]] = None):
        """Record user activity and update stats"""
        if data is None:
            data = {}
            
        now = datetime.now()
        
        # Update streak
        if self.user_stats.last_activity:
            last_date = datetime.fromisoformat(self.user_stats.last_activity).date()
            days_diff = (now.date() - last_date).days
            
            if days_diff == 1:  # Consecutive day
                self.user_stats.current_streak += 1
            elif days_diff > 1:  # Streak broken
                self.user_stats.current_streak = 1
            # Same day - no change to streak
        else:
            self.user_stats.current_streak = 1
        
        self.user_stats.longest_streak = max(self.user_stats.longest_streak, self.user_stats.current_streak)
        self.user_stats.last_activity = now.isoformat()
        
        # Handle specific activities
        if activity_type == "program_written":
            self.user_stats.programs_written += 1
            self.user_stats.lines_of_code += data.get("lines", 0)
            language = data.get("language", "unknown")
            if self.user_stats.languages_used is None:
                self.user_stats.languages_used = {}
            self.user_stats.languages_used[language] = self.user_stats.languages_used.get(language, 0) + 1
            
        elif activity_type == "tutorial_completed":
            self.user_stats.tutorials_finished += 1
            
        elif activity_type == "challenge_completed":
            self.user_stats.challenges_completed += 1
            completion_time = data.get("time", None)
            if completion_time:
                challenge_id = data.get("challenge_id")
                if challenge_id in self.challenges:
                    challenge = self.challenges[challenge_id]
                    if challenge.best_time is None or completion_time < challenge.best_time:
                        challenge.best_time = completion_time
        
        # Award points and experience
        points_earned = data.get("points", 0)
        self.user_stats.total_points += points_earned
        self.user_stats.experience += points_earned
        
        # Check for level up
        old_level = self.user_stats.level
        self.user_stats.level = self.calculate_level(self.user_stats.experience)
        
        if self.user_stats.level > old_level and self.level_up_callback:
            self.level_up_callback(old_level, self.user_stats.level)
        
        # Check achievements
        newly_unlocked = self.check_achievements()
        
        # Save data
        self.save_data()
        
        # Trigger callbacks
        if newly_unlocked and self.achievement_callback:
            for achievement in newly_unlocked:
                self.achievement_callback(achievement)
                
        if self.stats_update_callback:
            self.stats_update_callback(self.user_stats)

    def calculate_level(self, experience: int) -> int:
        """Calculate user level based on experience points"""
        # Level progression: 100 XP for level 2, then increases by 50 each level
        if experience < 100:
            return 1
        
        level = 1
        xp_needed = 100
        remaining_xp = experience
        
        while remaining_xp >= xp_needed:
            remaining_xp -= xp_needed
            level += 1
            xp_needed += 50  # Each level requires 50 more XP than the previous
        
        return level

    def get_xp_for_next_level(self) -> int:
        """Get XP needed for next level"""
        current_level = self.user_stats.level
        total_xp_needed = 0
        
        for i in range(1, current_level + 1):
            if i == 1:
                continue
            total_xp_needed += 100 + (i - 2) * 50
        
        next_level_xp = 100 + (current_level - 1) * 50
        current_level_progress = self.user_stats.experience - total_xp_needed
        
        return next_level_xp - current_level_progress

    def check_achievements(self) -> List[Achievement]:
        """Check and unlock new achievements"""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue
                
            # Check requirements
            requirements_met = True
            
            for req_type, req_value in achievement.requirements.items():
                if req_type == "programs_written":
                    if self.user_stats.programs_written < req_value:
                        requirements_met = False
                        achievement.progress = self.user_stats.programs_written / req_value
                        
                elif req_type == "tutorials_completed":
                    if self.user_stats.tutorials_finished < req_value:
                        requirements_met = False
                        achievement.progress = self.user_stats.tutorials_finished / req_value
                        
                elif req_type == "streak_days":
                    if self.user_stats.current_streak < req_value:
                        requirements_met = False
                        achievement.progress = self.user_stats.current_streak / req_value
                        
                elif req_type == "languages_used":
                    languages_count = len(self.user_stats.languages_used) if self.user_stats.languages_used else 0
                    if languages_count < req_value:
                        requirements_met = False
                        achievement.progress = languages_count / req_value
                        
                # Add more requirement checks as needed
            
            if requirements_met:
                achievement.unlocked = True
                achievement.unlock_date = datetime.now().isoformat()
                achievement.progress = 1.0
                self.user_stats.total_points += achievement.points
                newly_unlocked.append(achievement)
        
        return newly_unlocked

    def get_available_challenges(self, language: Optional[str] = None, difficulty: Optional[str] = None) -> List[Challenge]:
        """Get available challenges, optionally filtered"""
        challenges = list(self.challenges.values())
        
        if language:
            challenges = [c for c in challenges if c.language.lower() == language.lower()]
            
        if difficulty:
            challenges = [c for c in challenges if c.difficulty.lower() == difficulty.lower()]
        
        return sorted(challenges, key=lambda x: x.points)

    def start_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Start a specific challenge"""
        if challenge_id in self.challenges:
            challenge = self.challenges[challenge_id]
            challenge.attempts += 1
            return challenge
        return None

    def complete_challenge(self, challenge_id: str, user_code: str, completion_time: float) -> Dict[str, Any]:
        """Complete a challenge and award points"""
        if challenge_id not in self.challenges:
            return {"success": False, "message": "Challenge not found"}
        
        challenge = self.challenges[challenge_id]
        
        # Simple validation - in a real implementation, this would be more sophisticated
        passed_tests = 0
        for test_case in challenge.test_cases:
            # This is a simplified test - real implementation would execute the code
            if test_case["expected_output"] in user_code or "drawn" in test_case["expected_output"]:
                passed_tests += 1
        
        if passed_tests == len(challenge.test_cases):
            challenge.completed = True
            points_awarded = challenge.points
            
            # Bonus points for speed
            if challenge.time_limit and completion_time < challenge.time_limit * 0.5:
                points_awarded = int(points_awarded * 1.5)  # 50% bonus for fast completion
            
            self.record_activity("challenge_completed", {
                "challenge_id": challenge_id,
                "time": completion_time,
                "points": points_awarded
            })
            
            return {
                "success": True,
                "points_awarded": points_awarded,
                "message": f"Challenge completed! +{points_awarded} points",
                "fast_completion": completion_time < challenge.time_limit * 0.5 if challenge.time_limit else False
            }
        else:
            return {
                "success": False,
                "message": f"Challenge not completed. Passed {passed_tests}/{len(challenge.test_cases)} tests."
            }

    def get_leaderboard(self, category: str = "total_points") -> List[Dict[str, Any]]:
        """Get leaderboard data (simplified - would connect to database in real implementation)"""
        # This is a placeholder - real implementation would fetch from database
        return [
            {"username": "You", "score": getattr(self.user_stats, category, 0), "rank": 1}
        ]

    def get_daily_challenge(self) -> Optional[Challenge]:
        """Get today's daily challenge"""
        # Rotate through challenges based on day of year
        day_of_year = datetime.now().timetuple().tm_yday
        challenge_list = list(self.challenges.values())
        
        if challenge_list:
            daily_challenge = challenge_list[day_of_year % len(challenge_list)]
            return daily_challenge
        
        return None

    def get_user_dashboard(self) -> Dict[str, Any]:
        """Get complete user dashboard data"""
        unlocked_achievements = [a for a in self.achievements.values() if a.unlocked]
        in_progress_achievements = [a for a in self.achievements.values() if not a.unlocked and a.progress > 0]
        
        return {
            "stats": asdict(self.user_stats),
            "level": self.user_stats.level,
            "xp_to_next_level": self.get_xp_for_next_level(),
            "achievements": {
                "unlocked": len(unlocked_achievements),
                "total": len(self.achievements),
                "recent": sorted(unlocked_achievements, key=lambda x: x.unlock_date or "", reverse=True)[:5]
            },
            "challenges": {
                "completed": len([c for c in self.challenges.values() if c.completed]),
                "total": len(self.challenges),
                "daily": self.get_daily_challenge()
            },
            "in_progress_achievements": in_progress_achievements
        }

    def save_data(self):
        """Save gamification data to file"""
        try:
            self.data_file.parent.mkdir(exist_ok=True)
            
            data = {
                "user_stats": asdict(self.user_stats),
                "achievements": {
                    aid: asdict(achievement) for aid, achievement in self.achievements.items()
                },
                "challenges": {
                    cid: asdict(challenge) for cid, challenge in self.challenges.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except (IOError, OSError, ValueError) as e:
            print(f"Error saving gamification data: {e}")

    def load_data(self):
        """Load gamification data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load user stats
                if "user_stats" in data:
                    stats_data = data["user_stats"]
                    self.user_stats = UserStats(**stats_data)
                
                # Load achievement progress
                if "achievements" in data:
                    for aid, ach_data in data["achievements"].items():
                        if aid in self.achievements:
                            for key, value in ach_data.items():
                                if hasattr(self.achievements[aid], key):
                                    setattr(self.achievements[aid], key, value)
                
                # Load challenge progress  
                if "challenges" in data:
                    for cid, ch_data in data["challenges"].items():
                        if cid in self.challenges:
                            for key, value in ch_data.items():
                                if hasattr(self.challenges[cid], key):
                                    setattr(self.challenges[cid], key, value)
                                    
        except (IOError, OSError, ValueError, json.JSONDecodeError) as e:
            print(f"Error loading gamification data: {e}")