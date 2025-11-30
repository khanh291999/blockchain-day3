from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pow_simulator import PoWSimulator
from pos_simulator import PoSSimulator
from fork_resolution import ForkResolutionSimulator

app = Flask(__name__)
CORS(app)

# Khởi tạo các simulator
pow_sim = PoWSimulator()
pos_sim = PoSSimulator()
fork_sim = ForkResolutionSimulator()

# Khởi tạo với dữ liệu mặc định
pow_sim.create_genesis_block()
pow_sim.add_miner("Miner Alpha", hash_power=100)
pow_sim.add_miner("Miner Beta", hash_power=150)
pow_sim.add_miner("Miner Gamma", hash_power=80)

pos_sim.add_validator("Validator A", stake=10)
pos_sim.add_validator("Validator B", stake=50)
pos_sim.add_validator("Validator C", stake=40)

fork_sim.create_initial_chain()

@app.route('/')
def index():
    """Phục vụ trang HTML chính"""
    return render_template('index.html')

# ==================== PoW Endpoints ====================

@app.route('/api/pow/mine', methods=['POST'])
def pow_mine():
    """Đào một block mới sử dụng PoW"""
    try:
        result = pow_sim.simulate_mining_race()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pow/blockchain', methods=['GET'])
def pow_blockchain():
    """Lấy blockchain PoW hiện tại"""
    return jsonify({
        'success': True,
        'data': pow_sim.get_blockchain()
    })

@app.route('/api/pow/miners', methods=['GET'])
def pow_miners():
    """Lấy thống kê cho tất cả các miner"""
    return jsonify({
        'success': True,
        'data': pow_sim.get_miners_stats()
    })

@app.route('/api/pow/add-miner', methods=['POST'])
def pow_add_miner():
    """Thêm một miner mới"""
    data = request.json
    name = data.get('name', f'Miner {len(pow_sim.miners) + 1}')
    hash_power = data.get('hash_power', 100)
    
    miner = pow_sim.add_miner(name, hash_power)
    
    return jsonify({
        'success': True,
        'data': {
            'name': miner.name,
            'hash_power': miner.hash_power
        }
    })

@app.route('/api/pow/reset', methods=['POST'])
def pow_reset():
    """Reset simulator PoW"""
    global pow_sim
    pow_sim = PoWSimulator()
    pow_sim.create_genesis_block()
    pow_sim.add_miner("Miner Alpha", hash_power=100)
    pow_sim.add_miner("Miner Beta", hash_power=150)
    pow_sim.add_miner("Miner Gamma", hash_power=80)
    
    return jsonify({
        'success': True,
        'message': 'PoW simulator đã được reset'
    })

# ==================== PoS Endpoints ====================

@app.route('/api/pos/validate', methods=['POST'])
def pos_validate():
    """Mô phỏng một lần validation"""
    try:
        result = pos_sim.simulate_validation()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pos/validate-multiple', methods=['POST'])
def pos_validate_multiple():
    """Mô phỏng nhiều lần validation để test weighted selection"""
    data = request.json
    count = data.get('count', 100)
    
    try:
        result = pos_sim.simulate_multiple_validations(count)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pos/validators', methods=['GET'])
def pos_validators():
    """Lấy thống kê cho tất cả các validator"""
    return jsonify({
        'success': True,
        'data': pos_sim.get_validators_stats()
    })

@app.route('/api/pos/add-validator', methods=['POST'])
def pos_add_validator():
    """Thêm một validator mới"""
    data = request.json
    name = data.get('name', f'Validator {len(pos_sim.validators) + 1}')
    stake = data.get('stake', 10)
    
    validator = pos_sim.add_validator(name, stake)
    
    return jsonify({
        'success': True,
        'data': validator.to_dict()
    })

@app.route('/api/pos/reset', methods=['POST'])
def pos_reset():
    """Reset simulator PoS"""
    global pos_sim
    pos_sim = PoSSimulator()
    pos_sim.add_validator("Validator A", stake=10)
    pos_sim.add_validator("Validator B", stake=50)
    pos_sim.add_validator("Validator C", stake=40)
    
    return jsonify({
        'success': True,
        'message': 'PoS simulator đã được reset'
    })

# ==================== Fork Resolution Endpoints ====================

@app.route('/api/fork/create', methods=['POST'])
def fork_create():
    """Tạo một tình huống fork"""
    try:
        result = fork_sim.simulate_fork_scenario()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fork/resolve', methods=['POST'])
def fork_resolve():
    """Giải quyết fork sử dụng longest chain rule"""
    try:
        result = fork_sim.apply_longest_chain_rule()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fork/chains', methods=['GET'])
def fork_chains():
    """Lấy tất cả các chain hiện tại"""
    return jsonify({
        'success': True,
        'data': fork_sim.get_all_chains()
    })

@app.route('/api/fork/history', methods=['GET'])
def fork_history():
    """Lấy lịch sử fork"""
    return jsonify({
        'success': True,
        'data': fork_sim.get_fork_history()
    })

@app.route('/api/fork/reset', methods=['POST'])
def fork_reset():
    """Reset simulator fork"""
    global fork_sim
    fork_sim = ForkResolutionSimulator()
    fork_sim.create_initial_chain()
    
    return jsonify({
        'success': True,
        'message': 'Fork simulator đã được reset'
    })

if __name__ == '__main__':
    print("🚀 Đang khởi động Blockchain Consensus Simulator...")
    print("📡 Server đang chạy tại: http://localhost:5000")
    print("🌐 Mở trình duyệt để xem simulation!")
    app.run(debug=True, host='0.0.0.0', port=5000)
