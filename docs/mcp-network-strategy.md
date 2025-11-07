# MCP接口设计方案

## 设计决策：分阶段网络支持策略

### 阶段1：本地MCP接口 (当前目标)

#### 设计原则
- **MCP协议纯度**: 严格遵循Model Context Protocol标准
- **本地优先**: 进程间通信，零网络延迟
- **API完整性**: 设计完整的三层决策API
- **扩展预留**: 为后续网络扩展预留接口

#### 核心接口设计
```python
# 三层决策API
class MCPWorkerInterface:
    # 战略层 (Strategic) - 低频决策
    async def strategic_resource_allocation(self, economy_ratio: float, military_ratio: float)
    async def strategic_expansion_timing(self, resource_threshold: int)
    async def strategic_building_priority(self, building_queue: List[BuildingType])
    
    # 战术层 (Tactical) - 中频决策  
    async def tactical_worker_assignment(self, workers: List[WorkerID], tasks: List[Task])
    async def tactical_resource_distribution(self, resource_points: List[ResourcePoint])
    async def tactical_base_defense(self, threat_level: ThreatAssessment)
    
    # 操作层 (Operational) - 高频决策
    async def operational_worker_move(self, worker_id: WorkerID, target_pos: Position)
    async def operational_worker_gather(self, worker_id: WorkerID, resource_point: ResourcePoint)
    async def operational_worker_return(self, worker_id: WorkerID, drop_point: Building)
```

#### 技术栈
- **MCP Server**: Python MCP SDK
- **通信**: 进程间通信 (stdin/stdout 或 named pipes)
- **协议**: 标准MCP JSON-RPC
- **集成**: 与现有IoC/AOP架构无缝集成

### 阶段2：网络扩展层 (后续目标)

#### 网络网关设计
```python
class MCPNetworkGateway:
    """网络MCP网关 - 将网络调用转换为本地MCP调用"""
    
    async def handle_websocket_connection(self, websocket):
        # 处理WebSocket连接的AI Agent
        
    async def handle_http_request(self, request):
        # 处理HTTP REST API调用
        
    async def forward_to_local_mcp(self, mcp_message):
        # 转发到本地MCP服务器
```

#### 网络协议支持
- **WebSocket**: 实时双向通信，适合AI Agent
- **HTTP REST**: 简单请求-响应，适合云端AI服务
- **TCP Socket**: 高性能二进制通信，适合集群训练

### 阶段3：分布式架构 (长期愿景)

#### 游戏协调器
```python
class DistributedGameCoordinator:
    """分布式游戏协调器"""
    
    async def coordinate_multi_agent_game(self, agents: List[AIAgent])
    async def synchronize_game_state(self, game_sessions: List[GameSession])
    async def load_balance_requests(self, agent_requests: List[Request])
```

## 当前实现建议

### 立即开始：本地MCP接口

**理由**:
1. **验证核心概念**: 先确保AI Agent能有效控制Worker
2. **API设计迭代**: 在本地环境快速迭代接口设计
3. **性能基准**: 建立无网络干扰的性能基准
4. **架构稳定**: 确保核心架构稳定后再添加网络层

**实现步骤**:
1. 设计MCP Tools API (3层决策接口)
2. 实现MCP Server (基于Python MCP SDK)
3. 集成到MinSC (IoC容器管理MCP服务)
4. 测试AI Agent控制Worker的基本功能
5. 性能优化和API完善

### 后续扩展：网络支持

**触发条件**:
- 本地MCP接口稳定运行
- AI Agent控制逻辑验证成功
- 需要支持远程AI或多人对战

**扩展策略**:
- 保持本地接口API不变
- 添加网络网关层
- 支持多种网络协议
- 向后兼容本地部署

## 技术架构预览

### 最终目标架构
```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent Layer                       │
│  ┌─────────────┬─────────────┬─────────────────────┐    │
│  │  Local AI   │  Remote AI  │  Cloud AI Service   │    │
│  └─────────────┴─────────────┴─────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                  Network Gateway                        │
│  ┌─────────────┬─────────────┬─────────────────────┐    │
│  │ WebSocket   │  HTTP REST  │   TCP Socket        │    │
│  └─────────────┴─────────────┴─────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    MCP Server                           │
│              (Model Context Protocol)                   │
├─────────────────────────────────────────────────────────┤
│                 IoC/AOP Container                       │
│              (MinSC Game Engine)                        │
└─────────────────────────────────────────────────────────┘
```

### 当前实现范围
```
┌─────────────────────────────────────────────────────────┐
│                  Local AI Agent                         │
├─────────────────────────────────────────────────────────┤
│                    MCP Server                           │ ← 当前目标
│              (Model Context Protocol)                   │
├─────────────────────────────────────────────────────────┤
│                 IoC/AOP Container                       │ ← 已完成
│              (MinSC Game Engine)                        │
└─────────────────────────────────────────────────────────┘
```

## 结论

**建议采用本地优先，网络预留的策略**：

1. **立即开始本地MCP接口设计** - 快速验证核心功能
2. **API设计考虑网络扩展** - 确保接口可以无缝扩展到网络
3. **后续添加网络网关** - 在核心功能稳定后支持网络调用

这样既能快速推进AI Agent控制验证，又为未来的分布式AI对战和云端AI服务预留了扩展空间。