import random
from typing import List, Dict

class Validator:
    """Đại diện cho một validator trong cơ chế đồng thuận PoS"""
    def __init__(self, name: str, stake: int):
        self.name = name
        self.stake = stake
        self.blocks_validated = 0
        self.rewards = 0
        
    def to_dict(self) -> Dict:
        """Chuyển đổi validator sang dictionary"""
        return {
            'name': self.name,
            'stake': self.stake,
            'blocks_validated': self.blocks_validated,
            'rewards': self.rewards
        }


class PoSSimulator:
    """Mô phỏng cơ chế đồng thuận Proof of Stake"""
    def __init__(self):
        self.validators: List[Validator] = []
        self.validation_history: List[Dict] = []
        
    def add_validator(self, name: str, stake: int):
        """Thêm một validator mới vào mạng"""
        validator = Validator(name, stake)
        self.validators.append(validator)
        return validator
    
    def weighted_random_selection(self) -> Validator:
        """
        Chọn validator bằng phương pháp weighted random selection
        Validator có stake cao hơn có xác suất được chọn cao hơn
        """
        if not self.validators:
            raise ValueError("Không có validator nào trong mạng")
        
        # Sử dụng số lượng stake làm trọng số
        stakes = [v.stake for v in self.validators]
        selected = random.choices(self.validators, weights=stakes, k=1)[0]
        
        return selected
    
    def simulate_validation(self) -> Dict:
        """
        Mô phỏng một lần validation block
        Trả về thông tin về ai đã validate và stake của họ
        """
        selected_validator = self.weighted_random_selection()
        selected_validator.blocks_validated += 1
        
        # Phần thưởng tỷ lệ với stake
        reward = selected_validator.stake * 0.1
        selected_validator.rewards += reward
        
        result = {
            'validator': selected_validator.name,
            'stake': selected_validator.stake,
            'reward': round(reward, 2),
            'total_blocks_validated': selected_validator.blocks_validated
        }
        
        self.validation_history.append(result)
        
        return result
    
    def simulate_multiple_validations(self, count: int) -> Dict:
        """
        Chạy nhiều vòng validation và trả về thống kê
        Được sử dụng để xác minh weighted random selection hoạt động đúng
        """
        results = []
        for _ in range(count):
            result = self.simulate_validation()
            results.append(result)
        
        # Tính toán thống kê
        stats = {}
        total_stake = sum(v.stake for v in self.validators)
        
        for validator in self.validators:
            validator_results = [r for r in results if r['validator'] == validator.name]
            count_selected = len(validator_results)
            percentage = (count_selected / count) * 100
            expected_percentage = (validator.stake / total_stake) * 100
            
            stats[validator.name] = {
                'times_selected': count_selected,
                'percentage': round(percentage, 1),
                'expected_percentage': round(expected_percentage, 1),
                'stake': validator.stake,
                'total_rewards': round(validator.rewards, 2)
            }
        
        return {
            'total_validations': count,
            'statistics': stats,
            'validators': [v.to_dict() for v in self.validators]
        }
    
    def get_validators_stats(self) -> List[Dict]:
        """Lấy thống kê hiện tại cho tất cả các validator"""
        total_stake = sum(v.stake for v in self.validators)
        total_validations = sum(v.blocks_validated for v in self.validators)
        
        return [
            {
                'name': v.name,
                'stake': v.stake,
                'stake_percentage': round((v.stake / total_stake) * 100, 1) if total_stake > 0 else 0,
                'blocks_validated': v.blocks_validated,
                'validation_percentage': round((v.blocks_validated / total_validations) * 100, 1) if total_validations > 0 else 0,
                'total_rewards': round(v.rewards, 2)
            }
            for v in self.validators
        ]
    
    def reset(self):
        """Reset tất cả thống kê của validators"""
        for validator in self.validators:
            validator.blocks_validated = 0
            validator.rewards = 0
        self.validation_history.clear()
