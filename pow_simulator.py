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
        
    def mine_block(self, block: Block, difficulty: int) -> tuple[Block, int, float]:
        """
        Đào một block bằng cách tìm nonce tạo ra hash với 'difficulty' số 0 đứng đầu
        Trả về: (block_đã_đào, số_lần_thử, thời_gian)
        """
        target = '0' * difficulty
        attempts = 0
        start_time = time.time()
        
        # Mỗi miner thử với tốc độ khác nhau dựa trên hash_power
        # Hash power cao = thử nhiều hơn trong cùng thời gian
        while True:
            # Thử một nonce ngẫu nhiên
            block.nonce = random.randint(0, 10000000)
            block.hash = block.calculate_hash()
            attempts += 1
            
            # Kiểm tra xem hash có đạt yêu cầu không
            if block.hash.startswith(target):
                elapsed_time = time.time() - start_time
                return block, attempts, elapsed_time
            
            # Mô phỏng tốc độ hash dựa trên hash_power
            # Hash power thấp = phải chờ lâu hơn giữa các lần thử
            if attempts % max(1, (200 - self.hash_power)) == 0:
                time.sleep(0.0001)  # Delay rất nhỏ


class PoWSimulator:
    """Mô phỏng cơ chế đồng thuận Proof of Work"""
    def __init__(self):
        self.blockchain: List[Block] = []
        self.miners: List[Miner] = []
        self.difficulty = 4
        self.target_time = 2.0  # Mục tiêu 2 giây mỗi block
        
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
        Điều chỉnh độ khó ngay lập tức dựa trên thời gian đào block hiện tại
        """
        # Điều chỉnh ngay sau mỗi block, không cần chờ 3 blocks
        
        # Nếu thời gian đào nhỏ hơn 50% mục tiêu, tăng độ khó
        if mining_time < self.target_time * 0.5:
            self.difficulty += 1
            return f"⬆️ Độ khó tăng lên {self.difficulty}"
        # Nếu thời gian đào lớn hơn 200% mục tiêu, giảm độ khó
        elif mining_time > self.target_time * 2.0 and self.difficulty > 1:
            self.difficulty -= 1
            return f"⬇️ Độ khó giảm xuống {self.difficulty}"
        
        return None
    
    def simulate_mining_race(self) -> Dict:
        """
        Mô phỏng cuộc đua THỰC SỰ giữa các miner để tìm block tiếp theo
        Tất cả miners cùng đua, ai tìm ra nonce trước thì thắng
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
        
        # ✅ ĐÚNG: Mô phỏng cuộc đua thực sự
        # Mỗi miner có một bản copy riêng của block để đào
        import threading
        import copy
        
        race_results = []
        race_lock = threading.Lock()
        race_finished = threading.Event()
        
        def mine_worker(miner, block_copy):
            """Worker thread cho mỗi miner"""
            try:
                mined_block, attempts, elapsed = miner.mine_block(block_copy, self.difficulty)
                
                with race_lock:
                    if not race_finished.is_set():
                        # Miner này thắng!
                        race_finished.set()
                        race_results.append({
                            'miner': miner,
                            'block': mined_block,
                            'attempts': attempts,
                            'elapsed': elapsed
                        })
            except Exception as e:
                pass
        
        # Khởi động tất cả miners cùng lúc
        threads = []
        for miner in self.miners:
            block_copy = Block(
                new_block.index,
                new_block.timestamp,
                new_block.data,
                new_block.previous_hash
            )
            thread = threading.Thread(target=mine_worker, args=(miner, block_copy))
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # Đợi có miner thắng
        race_finished.wait(timeout=30)  # Timeout 30s
        
        # Dừng tất cả threads khác
        for thread in threads:
            thread.join(timeout=0.1)
        
        if not race_results:
            # Fallback nếu không có kết quả
            return {'error': 'Mining timeout'}
        
        result = race_results[0]
        winner = result['miner']
        mined_block = result['block']
        attempts = result['attempts']
        mining_time = result['elapsed']
        
        # Cập nhật thống kê
        winner.blocks_mined += 1
        
        # Thêm block vào blockchain
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
