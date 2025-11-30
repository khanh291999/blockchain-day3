import hashlib
import time
import random
from typing import List, Dict, Optional

class Block:
    """Đại diện cho một block trong blockchain"""
    def __init__(self, index: int, timestamp: float, data: str, previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Tính toán hash SHA-256 của block"""
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Chuyển đổi block sang dictionary để serialize JSON"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class Miner:
    """Đại diện cho một thợ đào (miner) trong cơ chế đồng thuận PoW"""
    def __init__(self, name: str, hash_power: int):
        self.name = name
        self.hash_power = hash_power  # Số lượng hash mỗi lần thử
        self.blocks_mined = 0
        
    def mine_block(self, block: Block, difficulty: int) -> tuple[Block, int]:
        """
        Đào một block bằng cách tìm nonce tạo ra hash với 'difficulty' số 0 đứng đầu
        Trả về: (block_đã_đào, số_lần_thử)
        """
        target = '0' * difficulty
        attempts = 0
        
        while True:
            block.nonce = random.randint(0, 1000000)
            block.hash = block.calculate_hash()
            attempts += 1
            
            if block.hash.startswith(target):
                self.blocks_mined += 1
                return block, attempts
            
            # Mô phỏng hash power - miner mạnh hơn có thể thử nhiều nonce hơn
            if attempts % self.hash_power == 0:
                time.sleep(0.001)  # Delay nhỏ để mô phỏng


class PoWSimulator:
    """Mô phỏng cơ chế đồng thuận Proof of Work"""
    def __init__(self):
        self.blockchain: List[Block] = []
        self.miners: List[Miner] = []
        self.difficulty = 4
        self.target_time = 2.0  # Mục tiêu 2 giây mỗi block
        self.recent_block_times: List[float] = []
        
    def create_genesis_block(self):
        """Tạo block đầu tiên trong blockchain"""
        genesis = Block(0, time.time(), "Genesis Block", "0")
        self.blockchain.append(genesis)
        
    def add_miner(self, name: str, hash_power: int):
        """Thêm một miner mới vào mạng"""
        miner = Miner(name, hash_power)
        self.miners.append(miner)
        return miner
    
    def adjust_difficulty(self, mining_time: float):
        """
        Điều chỉnh độ khó: Nếu block được tìm thấy quá nhanh, tăng độ khó
        """
        self.recent_block_times.append(mining_time)
        
        # Chỉ giữ lại 3 thời gian block gần nhất
        if len(self.recent_block_times) > 3:
            self.recent_block_times.pop(0)
        
        if len(self.recent_block_times) >= 3:
            avg_time = sum(self.recent_block_times) / len(self.recent_block_times)
            
            # Nếu thời gian trung bình nhỏ hơn 50% mục tiêu, tăng độ khó
            if avg_time < self.target_time * 0.5:
                self.difficulty += 1
                return f"⬆️ Độ khó tăng lên {self.difficulty}"
            # Nếu thời gian trung bình lớn hơn 200% mục tiêu, giảm độ khó
            elif avg_time > self.target_time * 2.0 and self.difficulty > 1:
                self.difficulty -= 1
                return f"⬇️ Độ khó giảm xuống {self.difficulty}"
        
        return None
    
    def simulate_mining_race(self) -> Dict:
        """
        Mô phỏng cuộc đua giữa các miner để tìm block tiếp theo
        Trả về thông tin chi tiết về quá trình đào
        """
        if not self.blockchain:
            self.create_genesis_block()
        
        last_block = self.blockchain[-1]
        new_block = Block(
            index=len(self.blockchain),
            timestamp=time.time(),
            data=f"Block {len(self.blockchain)} data",
            previous_hash=last_block.hash
        )
        
        # Chọn ngẫu nhiên miner chiến thắng (có trọng số theo hash power)
        total_hash_power = sum(m.hash_power for m in self.miners)
        winner = random.choices(
            self.miners, 
            weights=[m.hash_power for m in self.miners]
        )[0]
        
        start_time = time.time()
        mined_block, attempts = winner.mine_block(new_block, self.difficulty)
        mining_time = time.time() - start_time
        
        self.blockchain.append(mined_block)
        
        # Kiểm tra điều chỉnh độ khó
        adjustment_msg = self.adjust_difficulty(mining_time)
        
        return {
            'block': mined_block.to_dict(),
            'winner': winner.name,
            'attempts': attempts,
            'mining_time': round(mining_time, 2),
            'difficulty': self.difficulty,
            'adjustment': adjustment_msg,
            'blockchain_length': len(self.blockchain)
        }
    
    def get_blockchain(self) -> List[Dict]:
        """Lấy toàn bộ blockchain"""
        return [block.to_dict() for block in self.blockchain]
    
    def get_miners_stats(self) -> List[Dict]:
        """Lấy thống kê cho tất cả các miner"""
        return [
            {
                'name': miner.name,
                'hash_power': miner.hash_power,
                'blocks_mined': miner.blocks_mined
            }
            for miner in self.miners
        ]
