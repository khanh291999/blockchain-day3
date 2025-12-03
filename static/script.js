// ==================== Global State ====================
let currentTab = 'pow';
const API_BASE = window.location.origin + '/api';

// ==================== Tab Switching ====================
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-gradient-to-r', 'from-indigo-600', 'to-purple-600', 'text-white');
        btn.classList.add('bg-white/95', 'backdrop-blur-lg', 'text-gray-700');
    });
    event.target.closest('.tab-btn').classList.remove('bg-white/95', 'backdrop-blur-lg', 'text-gray-700');
    event.target.closest('.tab-btn').classList.add('bg-gradient-to-r', 'from-indigo-600', 'to-purple-600', 'text-white');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    
    // Load tab data
    if (tabName === 'pow') {
        loadPoWData();
    } else if (tabName === 'pos') {
        loadPoSData();
    } else if (tabName === 'fork') {
        loadForkData();
    }
}

// ==================== PoW Functions ====================
async function loadPoWData() {
    try {
        const [blockchain, miners] = await Promise.all([
            fetch(`${API_BASE}/pow/blockchain`).then(r => r.json()),
            fetch(`${API_BASE}/pow/miners`).then(r => r.json())
        ]);
        
        if (blockchain.success) {
            renderPoWBlockchain(blockchain.data);
            updatePoWStats(blockchain.data);
        }
        
        if (miners.success) {
            renderMiners(miners.data);
        }
    } catch (error) {
        console.error('Error loading PoW data:', error);
    }
}

async function mineBlock() {
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
    btn.textContent = '⛏️ Mining...';
    
    try {
        const response = await fetch(`${API_BASE}/pow/mine`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showPoWResult(data.data);
            await loadPoWData();
        }
    } catch (error) {
        console.error('Error mining block:', error);
        alert('Error mining block: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
        btn.textContent = '⛏️ Mine Block';
    }
}

function renderPoWBlockchain(blockchain) {
    const container = document.getElementById('pow-blockchain');
    
    if (!blockchain || blockchain.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center">No blocks yet</p>';
        return;
    }
    
    container.innerHTML = blockchain.map((block, idx) => `
        <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl p-6 relative animate-block-appear">
            <div class="flex justify-between items-center mb-3">
                <span class="text-xl font-bold">Block #${block.index}</span>
                <span class="text-sm bg-white/20 px-3 py-1 rounded-full">Nonce: ${block.nonce}</span>
            </div>
            <div class="mb-3 font-medium">${block.data}</div>
            <div class="bg-white/10 p-3 rounded-lg font-mono text-sm break-all mb-2">
                🔒 Hash: ${block.hash}
            </div>
            <div class="bg-white/10 p-3 rounded-lg font-mono text-sm break-all">
                🔗 Previous: ${block.previous_hash}
            </div>
            ${idx < blockchain.length - 1 ? '<div class="absolute left-1/2 -bottom-4 transform -translate-x-1/2 text-2xl">⬇️</div>' : ''}
        </div>
    `).join('');
}

function renderMiners(miners) {
    const container = document.getElementById('pow-miners');
    
    const totalBlocks = miners.reduce((sum, m) => sum + m.blocks_mined, 0);
    
    container.innerHTML = miners.map(miner => {
        const percentage = totalBlocks > 0 ? (miner.blocks_mined / totalBlocks * 100) : 0;
        
        return `
            <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl p-5 animate-slide-in">
                <div class="flex justify-between items-center mb-3">
                    <span class="text-xl font-bold">${miner.name}</span>
                </div>
                <div class="flex gap-5 text-sm mb-3">
                    <span>⚡ Hash Power: ${miner.hash_power}</span>
                    <span>⛏️ Blocks: ${miner.blocks_mined}</span>
                </div>
                <div class="w-full h-2 bg-white/30 rounded-full overflow-hidden">
                    <div class="h-full bg-white rounded-full transition-all duration-300" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function updatePoWStats(blockchain) {
    const length = blockchain.length;
    document.getElementById('pow-length').textContent = length;
}

function updateDifficultyAdjustment(adjustment) {
    const element = document.getElementById('pow-adjustment');
    if (adjustment) {
        element.innerHTML = adjustment;
        element.classList.remove('text-indigo-600');
        element.classList.add('text-green-600');
    }
}

function showPoWResult(result) {
    const card = document.getElementById('pow-result');
    const content = document.getElementById('pow-result-content');
    
    // Update mining time with status
    const targetTime = 2.0;
    const miningTime = result.mining_time;
    const timeElement = document.getElementById('pow-mining-time');
    
    let timeStatus = '';
    let timeColor = 'text-indigo-600';
    
    if (miningTime < targetTime * 0.5) {
        timeStatus = '⚡ Quá nhanh!';
        timeColor = 'text-red-600';
    } else if (miningTime < targetTime) {
        timeStatus = '✅ Ổn định';
        timeColor = 'text-green-600';
    } else if (miningTime < targetTime * 2.0) {
        timeStatus = '⏱️ Bình thường';
        timeColor = 'text-blue-600';
    } else {
        timeStatus = '🐌 Chậm';
        timeColor = 'text-orange-600';
    }
    
    timeElement.innerHTML = `${miningTime}s - ${timeStatus}`;
    timeElement.className = `text-lg font-bold ${timeColor}`;
    
    // Update difficulty adjustment in stats section
    if (result.adjustment) {
        updateDifficultyAdjustment(result.adjustment);
    } else {
        const element = document.getElementById('pow-adjustment');
        element.innerHTML = '✅ Giữ nguyên';
        element.classList.remove('text-green-600');
        element.classList.add('text-indigo-600');
    }
    
    // Update difficulty display
    document.getElementById('pow-difficulty').textContent = result.difficulty;
    
    content.innerHTML = `
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Winner:</span>
            <span class="text-lg text-gray-900">🏆 ${result.winner}</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Mining Time:</span>
            <span class="text-lg text-gray-900">⏱️ ${result.mining_time}s</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Attempts:</span>
            <span class="text-lg text-gray-900">🔢 ${result.attempts}</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Current Difficulty:</span>
            <span class="text-lg text-gray-900">📊 ${result.difficulty}</span>
        </div>
        ${result.adjustment ? `
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg text-blue-800">
                ${result.adjustment}
            </div>
        ` : ''}
    `;
    
    card.classList.remove('hidden');
    document.getElementById('pow-difficulty').textContent = result.difficulty;
}

async function resetPoW() {
    if (!confirm('Reset PoW simulator?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/pow/reset`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('pow-result').classList.add('hidden');
            await loadPoWData();
        }
    } catch (error) {
        console.error('Error resetting PoW:', error);
    }
}

// ==================== PoS Functions ====================
async function loadPoSData() {
    try {
        const response = await fetch(`${API_BASE}/pos/validators`);
        const data = await response.json();
        
        if (data.success) {
            renderValidators(data.data);
            renderPoSChart(data.data);
        }
    } catch (error) {
        console.error('Error loading PoS data:', error);
    }
}

async function validateBlock() {
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
    btn.textContent = '⏳ Validating...';
    
    try {
        const response = await fetch(`${API_BASE}/pos/validate`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showPoSResult(data.data);
            await loadPoSData();
        }
    } catch (error) {
        console.error('Error validating block:', error);
        alert('Error validating block: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
        btn.textContent = '✅ Validate Block';
    }
}

async function runPoSTest(count = 100) {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
    
    // Format count with commas
    const formattedCount = count.toLocaleString();
    btn.textContent = `🧪 Running ${formattedCount} tests...`;
    
    const startTime = Date.now();
    
    try {
        const response = await fetch(`${API_BASE}/pos/validate-multiple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ count: count })
        });
        const data = await response.json();
        
        if (data.success) {
            const duration = ((Date.now() - startTime) / 1000).toFixed(2);
            data.data.duration = duration;
            data.data.count = count;
            showPoSTestResult(data.data);
            await loadPoSData();
        }
    } catch (error) {
        console.error('Error running PoS test:', error);
        alert('Error running test: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
        btn.textContent = originalText;
    }
}

function renderValidators(validators) {
    const container = document.getElementById('pos-validators');
    
    container.innerHTML = validators.map(validator => {
        return `
            <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl p-5 animate-slide-in">
                <div class="flex justify-between items-center mb-3">
                    <span class="text-xl font-bold">${validator.name}</span>
                </div>
                <div class="flex flex-wrap gap-4 text-sm mb-2">
                    <span>💰 Stake: ${validator.stake} coins (${validator.stake_percentage}%)</span>
                    <span>✅ Validated: ${validator.blocks_validated} (${validator.validation_percentage}%)</span>
                </div>
                <div class="text-sm mb-3">
                    <span>🎁 Rewards: ${validator.total_rewards} coins</span>
                </div>
                <div class="w-full h-2 bg-white/30 rounded-full overflow-hidden">
                    <div class="h-full bg-white rounded-full transition-all duration-300" style="width: ${validator.validation_percentage}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderPoSChart(validators) {
    const container = document.getElementById('pos-chart-container');
    
    if (!validators || validators.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center">No data yet</p>';
        return;
    }
    
    // Create a simple bar chart
    const maxPercentage = Math.max(...validators.map(v => Math.max(v.stake_percentage, v.validation_percentage)));
    
    container.innerHTML = `
        <div class="flex flex-col gap-6 p-4">
            ${validators.map(v => `
                <div>
                    <div class="font-semibold text-gray-800 mb-2">${v.name}</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <div class="text-sm text-gray-600 mb-1">Expected: ${v.stake_percentage}%</div>
                            <div class="bg-gray-200 h-8 rounded-lg overflow-hidden">
                                <div class="bg-gradient-to-r from-indigo-600 to-purple-600 h-full flex items-center justify-center text-white font-semibold text-sm transition-all duration-500" style="width: ${v.stake_percentage}%">
                                    ${v.stake_percentage}%
                                </div>
                            </div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600 mb-1">Actual: ${v.validation_percentage}%</div>
                            <div class="bg-gray-200 h-8 rounded-lg overflow-hidden">
                                <div class="bg-gradient-to-r from-green-500 to-emerald-600 h-full flex items-center justify-center text-white font-semibold text-sm transition-all duration-500" style="width: ${v.validation_percentage}%">
                                    ${v.validation_percentage}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function showPoSResult(result) {
    const card = document.getElementById('pos-result');
    const content = document.getElementById('pos-result-content');
    
    content.innerHTML = `
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg text-green-800 mb-4">
            🎉 Block validated successfully!
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Selected Validator:</span>
            <span class="text-lg text-gray-900">👤 ${result.validator}</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Stake Amount:</span>
            <span class="text-lg text-gray-900">💰 ${result.stake} coins</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Reward Earned:</span>
            <span class="text-lg text-gray-900">🎁 ${result.reward} coins</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Total Blocks Validated:</span>
            <span class="text-lg text-gray-900">✅ ${result.total_blocks_validated}</span>
        </div>
    `;
    
    card.classList.remove('hidden');
}

function showPoSTestResult(result) {
    const card = document.getElementById('pos-test-result');
    const content = document.getElementById('pos-test-content');
    
    const stats = result.statistics;
    const formattedCount = result.count ? result.count.toLocaleString() : result.total_validations.toLocaleString();
    const duration = result.duration ? ` in ${result.duration}s` : '';
    
    content.innerHTML = `
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg text-green-800 mb-4">
            ✅ Test completed! ${formattedCount} validations simulated${duration}.
        </div>
        ${Object.entries(stats).map(([name, data]) => {
            const diff = Math.abs(data.percentage - data.expected_percentage);
            const isClose = diff <= 10;
            
            return `
                <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-4">
                    <div class="mb-3">
                        <strong class="text-lg text-gray-900">${name}</strong>
                        <span class="ml-2 text-2xl">${isClose ? '✅' : '⚠️'}</span>
                    </div>
                    <div class="space-y-1 text-gray-700">
                        <div>Stake: ${data.stake} coins (${data.expected_percentage}%)</div>
                        <div>Times Selected: ${data.times_selected} (${data.percentage}%)</div>
                        <div>Expected: ~${data.expected_percentage}%</div>
                        <div>Total Rewards: ${data.total_rewards} coins</div>
                    </div>
                    ${!isClose ? `<div class="bg-yellow-50 border-l-4 border-yellow-500 p-3 rounded-lg text-yellow-800 mt-3">Deviation: ${diff.toFixed(1)}%</div>` : ''}
                </div>
            `;
        }).join('')}
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg text-blue-800">
            💡 The validator with 50 coins should win approximately 50% of the time.
            ${stats['Validator B'] && Math.abs(stats['Validator B'].percentage - 50) <= 10 ? 
                '✅ Test passed! The results match the expected distribution.' : 
                '⚠️ Run more validations for more accurate results.'}
        </div>
    `;
    
    card.classList.remove('hidden');
}

async function resetPoS() {
    if (!confirm('Reset PoS simulator?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/pos/reset`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('pos-result').classList.add('hidden');
            document.getElementById('pos-test-result').classList.add('hidden');
            await loadPoSData();
        }
    } catch (error) {
        console.error('Error resetting PoS:', error);
    }
}

// ==================== Fork Resolution Functions ====================
async function loadForkData() {
    try {
        const response = await fetch(`${API_BASE}/fork/chains`);
        const data = await response.json();
        
        if (data.success) {
            renderChains(data.data);
        }
    } catch (error) {
        console.error('Error loading fork data:', error);
    }
}

async function createFork() {
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
    btn.textContent = '🔱 Creating Fork...';
    
    try {
        const response = await fetch(`${API_BASE}/fork/create`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showForkResult(data.data);
            await loadForkData();
        }
    } catch (error) {
        console.error('Error creating fork:', error);
        alert('Error creating fork: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
        btn.textContent = '🔱 Create Fork';
    }
}

async function resolveFork() {
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
    btn.textContent = '⚖️ Resolving...';
    
    try {
        const response = await fetch(`${API_BASE}/fork/resolve`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            if (data.data.error) {
                alert(data.data.error);
            } else {
                showForkResolution(data.data);
                await loadForkData();
            }
        }
    } catch (error) {
        console.error('Error resolving fork:', error);
        alert('Error resolving fork: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed', 'animate-pulse-slow');
        btn.textContent = '⚖️ Resolve Fork';
    }
}

function renderChains(chains) {
    const container = document.getElementById('fork-chains');
    
    if (!chains || chains.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center">No chains yet. Create a fork to begin.</p>';
        return;
    }
    
    container.innerHTML = chains.map(chain => {
        const isWinner = chain.name.includes('Resolved');
        
        return `
            <div class="border-4 ${isWinner ? 'border-green-500 bg-green-50' : 'border-indigo-600 bg-gray-50'} rounded-2xl p-6">
                <div class="flex justify-between items-center mb-4 pb-4 border-b-2 border-gray-200">
                    <span class="text-xl font-bold text-gray-900">${chain.name}</span>
                    <span class="px-4 py-2 ${isWinner ? 'bg-green-500' : 'bg-indigo-600'} text-white rounded-full font-semibold">
                        📊 ${chain.length} blocks
                    </span>
                </div>
                <div class="flex gap-3 overflow-x-auto py-3">
                    ${chain.blocks.map((block, idx) => `
                        <div class="min-w-[80px] h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg" title="Block #${block.index}">
                            #${block.index}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function showForkResult(result) {
    const card = document.getElementById('fork-result');
    const content = document.getElementById('fork-result-content');
    
    content.innerHTML = `
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg text-yellow-800 mb-4">
            ⚠️ Fork detected! Two blocks were produced simultaneously due to network latency.
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Fork A:</span>
            <span class="text-lg text-gray-900">
                ${result.fork_a.length} blocks 
                (Miner A delay: ${result.miner_a_delay}s)
            </span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Fork B:</span>
            <span class="text-lg text-gray-900">
                ${result.fork_b.length} blocks 
                (Miner B delay: ${result.miner_b_delay}s)
            </span>
        </div>
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg text-blue-800">
            💡 Use "Resolve Fork" button to apply the Longest Chain Rule
        </div>
    `;
    
    card.classList.remove('hidden');
    document.getElementById('fork-resolution').classList.add('hidden');
}

function showForkResolution(result) {
    const card = document.getElementById('fork-resolution');
    const content = document.getElementById('fork-resolution-content');
    
    content.innerHTML = `
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg text-green-800 mb-4">
            ✅ Fork resolved successfully using ${result.resolution_rule}!
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Winning Chain:</span>
            <span class="text-lg text-gray-900">🏆 ${result.winner}</span>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
            <span class="block text-sm font-semibold text-gray-700 mb-1">Chain Length:</span>
            <span class="text-lg text-gray-900">📊 ${result.winner_length} blocks</span>
        </div>
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg text-blue-800 mb-4">
            💡 ${result.explanation}
        </div>
        <h4 class="text-xl font-bold text-gray-800 mt-6 mb-4">Chains Compared:</h4>
        ${result.chains_compared.map(chain => `
            <div class="p-4 bg-gray-50 rounded-xl border-l-4 border-indigo-600 mb-3">
                <span class="block text-sm font-semibold text-gray-700 mb-1">${chain.name}:</span>
                <span class="text-lg text-gray-900">
                    ${chain.length} blocks 
                    ${chain.is_winner ? '🏆 WINNER' : '❌ Discarded'}
                </span>
            </div>
        `).join('')}
    `;
    
    card.classList.remove('hidden');
}

async function resetFork() {
    if (!confirm('Reset Fork simulator?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/fork/reset`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('fork-result').classList.add('hidden');
            document.getElementById('fork-resolution').classList.add('hidden');
            await loadForkData();
        }
    } catch (error) {
        console.error('Error resetting Fork:', error);
    }
}

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', () => {
    loadPoWData();
});
