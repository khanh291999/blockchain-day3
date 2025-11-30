import time
import random
from typing import List, Dict, Optional
from pow_simulator import Block

class Blockchain:
    """Đại diện cho một blockchain (có thể là một nhánh fork)"""
    def __init__(self, name: str):
        self.name = name
        self.chain: List[Block] = []
        
    def add_block(self, block: Block):
        """Thêm một block vào chain này"""
        self.chain.append(block)
        
    def get_length(self) -> int:
        """Lấy độ dài của chain này"""
        return len(self.chain)
    
    def get_last_block(self) -> Optional[Block]:
        """Lấy block cuối cùng trong chain"""
        return self.chain[-1] if self.chain else None
    
    def to_dict(self) -> Dict:
        """Chuyển đổi blockchain sang dictionary"""
        return {
            'name': self.name,
            'length': self.get_length(),
            'blocks': [block.to_dict() for block in self.chain]
        }


class ForkResolutionSimulator:
    """Mô phỏng giải quyết fork sử dụng Longest Chain Rule"""
    def __init__(self):
        self.blockchains: List[Blockchain] = []
        self.network_latency_min = 0.5  # giây
        self.network_latency_max = 2.0  # giây
        self.fork_events: List[Dict] = []
        
    def create_initial_chain(self):
        """Tạo blockchain ban đầu với genesis block"""
        chain = Blockchain("Main Chain")
        genesis = Block(0, time.time(), "Genesis Block", "0")
        chain.add_block(genesis)
        self.blockchains = [chain]
        return chain
    
    def simulate_network_latency(self) -> float:
        """Mô phỏng độ trễ mạng ngẫu nhiên"""
        return random.uniform(self.network_latency_min, self.network_latency_max)
    
    def simulate_fork_scenario(self) -> Dict:
        """
        Mô phỏng tình huống fork khi hai block được tạo đồng thời
        do độ trễ mạng
        """
        if not self.blockchains:
            self.create_initial_chain()
        
        main_chain = self.blockchains[0]
        last_block = main_chain.get_last_block()
        
        # Mô phỏng hai miner tạo block gần như cùng lúc
        miner_a_delay = self.simulate_network_latency()
        miner_b_delay = self.simulate_network_latency()
        
        # Cả hai miner đều bắt đầu từ cùng một block trước đó
        block_a = Block(
            index=len(main_chain.chain),
            timestamp=time.time() + miner_a_delay,
            data=f"Block by Miner A (delay: {miner_a_delay:.2f}s)",
            previous_hash=last_block.hash,
            nonce=random.randint(1000, 9999)
        )
        
        block_b = Block(
            index=len(main_chain.chain),
            timestamp=time.time() + miner_b_delay,
            data=f"Block by Miner B (delay: {miner_b_delay:.2f}s)",
            previous_hash=last_block.hash,
            nonce=random.randint(1000, 9999)
        )
        
        # Tạo hai nhánh fork
        fork_a = Blockchain("Fork A")
        fork_a.chain = main_chain.chain.copy()
        fork_a.add_block(block_a)
        
        fork_b = Blockchain("Fork B")
        fork_b.chain = main_chain.chain.copy()
        fork_b.add_block(block_b)
        
        # Thêm ngẫu nhiên thêm block vào mỗi fork để tạo độ dài khác nhau
        # Điều này mô phỏng việc tiếp tục đào trên cả hai nhánh
        additional_blocks_a = random.randint(0, 2)
        additional_blocks_b = random.randint(0, 2)
        
        for i in range(additional_blocks_a):
            last = fork_a.get_last_block()
            new_block = Block(
                index=len(fork_a.chain),
                timestamp=time.time() + self.simulate_network_latency(),
                data=f"Additional block {i+1} on Fork A",
                previous_hash=last.hash,
                nonce=random.randint(1000, 9999)
            )
            fork_a.add_block(new_block)
        
        for i in range(additional_blocks_b):
            last = fork_b.get_last_block()
            new_block = Block(
                index=len(fork_b.chain),
                timestamp=time.time() + self.simulate_network_latency(),
                data=f"Additional block {i+1} on Fork B",
                previous_hash=last.hash,
                nonce=random.randint(1000, 9999)
            )
            fork_b.add_block(new_block)
        
        self.blockchains = [fork_a, fork_b]
        
        fork_event = {
            'timestamp': time.time(),
            'fork_a': fork_a.to_dict(),
            'fork_b': fork_b.to_dict(),
            'miner_a_delay': round(miner_a_delay, 2),
            'miner_b_delay': round(miner_b_delay, 2),
            'additional_blocks_a': additional_blocks_a,
            'additional_blocks_b': additional_blocks_b
        }
        
        self.fork_events.append(fork_event)
        
        return fork_event
    
    def apply_longest_chain_rule(self) -> Dict:
        """
        Áp dụng Longest Chain Rule để giải quyết fork
        Chain có nhiều block nhất (công việc tích lũy nhiều nhất) trở thành chain chính
        """
        if len(self.blockchains) < 2:
            return {
                'error': 'Không có fork để giải quyết. Vui lòng tạo fork trước.'
            }
        
        # Tìm chain dài nhất
        longest_chain = max(self.blockchains, key=lambda bc: bc.get_length())
        
        # Tìm tất cả các chain và độ dài của chúng để so sánh
        chains_info = [
            {
                'name': chain.name,
                'length': chain.get_length(),
                'is_winner': chain == longest_chain
            }
            for chain in self.blockchains
        ]
        
        # Đặt chain dài nhất làm chain chính
        self.blockchains = [longest_chain]
        longest_chain.name = "Main Chain (Resolved)"
        
        result = {
            'winner': longest_chain.name,
            'winner_length': longest_chain.get_length(),
            'chains_compared': chains_info,
            'resolved_chain': longest_chain.to_dict(),
            'resolution_rule': 'Longest Chain Rule',
            'explanation': f'Chain có {longest_chain.get_length()} blocks được chọn vì có nhiều proof-of-work tích lũy nhất'
        }
        
        return result
    
    def get_all_chains(self) -> List[Dict]:
        """Lấy thông tin về tất cả các chain hiện tại"""
        return [chain.to_dict() for chain in self.blockchains]
    
    def get_fork_history(self) -> List[Dict]:
        """Lấy lịch sử của tất cả các sự kiện fork"""
        return self.fork_events
    
    def reset(self):
        """Reset simulator"""
        self.blockchains = []
        self.fork_events = []
        self.create_initial_chain()
