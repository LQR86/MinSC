# MinSC MCP接口设计文档

## 概述

基于Model Context Protocol (MCP) 为AI Agent提供控制MinSC游戏中Worker单位的标准化接口。采用三层决策架构：Strategic (战略层)、Tactical (战术层)、Operational (操作层)。

## 接口架构

### 三层决策模型

```
┌─────────────────────────────────────────────────────────┐
│                 Strategic Layer                         │
│        (低频决策 - 资源分配、扩张时机、建筑优先级)        │
├─────────────────────────────────────────────────────────┤
│                 Tactical Layer                          │
│      (中频决策 - 工人分配、资源分布、区域控制)           │
├─────────────────────────────────────────────────────────┤
│                Operational Layer                        │
│       (高频决策 - 单位移动、采集指令、返回指令)          │
└─────────────────────────────────────────────────────────┘
```

### MCP Tools 定义

## 1. Strategic Layer Tools (战略层)

### 1.1 strategic_resource_allocation
**描述**: 设置经济与军事资源分配比例
```json
{
  "name": "strategic_resource_allocation",
  "description": "Set resource allocation strategy between economy and military",
  "inputSchema": {
    "type": "object",
    "properties": {
      "economy_ratio": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Ratio of resources allocated to economy (0.0-1.0)"
      },
      "military_ratio": {
        "type": "number", 
        "minimum": 0,
        "maximum": 1,
        "description": "Ratio of resources allocated to military (0.0-1.0)"
      }
    },
    "required": ["economy_ratio", "military_ratio"]
  }
}
```

### 1.2 strategic_expansion_timing
**描述**: 决定扩张到新资源点的时机
```json
{
  "name": "strategic_expansion_timing",
  "description": "Determine when to expand to new resource points",
  "inputSchema": {
    "type": "object",
    "properties": {
      "resource_threshold": {
        "type": "integer",
        "minimum": 0,
        "description": "Resource amount threshold to trigger expansion"
      },
      "worker_count_min": {
        "type": "integer",
        "minimum": 1,
        "description": "Minimum worker count before allowing expansion"
      }
    },
    "required": ["resource_threshold"]
  }
}
```

### 1.3 strategic_building_priority
**描述**: 设置建筑建造优先级
```json
{
  "name": "strategic_building_priority",
  "description": "Set building construction priority queue",
  "inputSchema": {
    "type": "object",
    "properties": {
      "building_queue": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["command_center", "barracks", "supply_depot"]
        },
        "description": "Ordered list of buildings to construct"
      }
    },
    "required": ["building_queue"]
  }
}
```

## 2. Tactical Layer Tools (战术层)

### 2.1 tactical_worker_assignment
**描述**: 分配工人到不同任务
```json
{
  "name": "tactical_worker_assignment",
  "description": "Assign workers to different tasks and resource points",
  "inputSchema": {
    "type": "object",
    "properties": {
      "assignments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "worker_id": {
              "type": "string",
              "description": "Unique worker identifier"
            },
            "task_type": {
              "type": "string",
              "enum": ["gather", "build", "idle", "scout"],
              "description": "Type of task to assign"
            },
            "target_id": {
              "type": "string",
              "description": "Target resource point or building ID"
            }
          },
          "required": ["worker_id", "task_type"]
        }
      }
    },
    "required": ["assignments"]
  }
}
```

### 2.2 tactical_resource_distribution
**描述**: 优化工人在资源点间的分布
```json
{
  "name": "tactical_resource_distribution",
  "description": "Optimize worker distribution across resource points",
  "inputSchema": {
    "type": "object",
    "properties": {
      "resource_assignments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "resource_point_id": {
              "type": "string",
              "description": "Resource point identifier"
            },
            "worker_count": {
              "type": "integer",
              "minimum": 0,
              "description": "Number of workers to assign to this resource point"
            },
            "priority": {
              "type": "integer",
              "minimum": 1,
              "maximum": 10,
              "description": "Priority level (1=low, 10=high)"
            }
          },
          "required": ["resource_point_id", "worker_count"]
        }
      }
    },
    "required": ["resource_assignments"]
  }
}
```

## 3. Operational Layer Tools (操作层)

### 3.1 operational_worker_move
**描述**: 命令特定工人移动到指定位置
```json
{
  "name": "operational_worker_move",
  "description": "Command a specific worker to move to target position",
  "inputSchema": {
    "type": "object",
    "properties": {
      "worker_id": {
        "type": "string",
        "description": "Unique worker identifier"
      },
      "target_position": {
        "type": "object",
        "properties": {
          "x": {"type": "number"},
          "y": {"type": "number"}
        },
        "required": ["x", "y"]
      },
      "move_type": {
        "type": "string",
        "enum": ["direct", "safe", "fastest"],
        "default": "direct",
        "description": "Type of movement pathfinding"
      }
    },
    "required": ["worker_id", "target_position"]
  }
}
```

### 3.2 operational_worker_gather
**描述**: 命令工人采集指定资源点
```json
{
  "name": "operational_worker_gather",
  "description": "Command worker to gather from specific resource point",
  "inputSchema": {
    "type": "object",
    "properties": {
      "worker_id": {
        "type": "string",
        "description": "Unique worker identifier"
      },
      "resource_point_id": {
        "type": "string", 
        "description": "Target resource point identifier"
      },
      "gather_amount": {
        "type": "integer",
        "minimum": 1,
        "description": "Amount to gather before returning (optional, default to max capacity)"
      }
    },
    "required": ["worker_id", "resource_point_id"]
  }
}
```

### 3.3 operational_worker_return
**描述**: 命令工人返回指定建筑卸载资源
```json
{
  "name": "operational_worker_return", 
  "description": "Command worker to return and unload resources at building",
  "inputSchema": {
    "type": "object",
    "properties": {
      "worker_id": {
        "type": "string",
        "description": "Unique worker identifier"
      },
      "target_building_id": {
        "type": "string",
        "description": "Target building ID for resource unloading"
      },
      "return_type": {
        "type": "string",
        "enum": ["immediate", "when_full", "when_safe"],
        "default": "immediate",
        "description": "Condition for return command"
      }
    },
    "required": ["worker_id", "target_building_id"]
  }
}
```

### 3.4 operational_batch_commands
**描述**: 批量执行多个操作层命令
```json
{
  "name": "operational_batch_commands",
  "description": "Execute multiple operational commands as a batch",
  "inputSchema": {
    "type": "object",
    "properties": {
      "commands": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "command_type": {
              "type": "string",
              "enum": ["move", "gather", "return"]
            },
            "worker_id": {"type": "string"},
            "parameters": {"type": "object"}
          },
          "required": ["command_type", "worker_id", "parameters"]
        }
      },
      "execution_mode": {
        "type": "string",
        "enum": ["parallel", "sequential"],
        "default": "parallel",
        "description": "How to execute the batch commands"
      }
    },
    "required": ["commands"]
  }
}
```

## 4. Query Tools (状态查询)

### 4.1 query_game_state
**描述**: 查询当前游戏状态
```json
{
  "name": "query_game_state",
  "description": "Get current game state information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_workers": {"type": "boolean", "default": true},
      "include_buildings": {"type": "boolean", "default": true},
      "include_resources": {"type": "boolean", "default": true},
      "player_id": {
        "type": "integer",
        "description": "Player ID to query (optional, default to current player)"
      }
    }
  }
}
```

### 4.2 query_worker_status
**描述**: 查询特定工人状态
```json
{
  "name": "query_worker_status",
  "description": "Get detailed status of specific worker",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "worker_id": {
        "type": "string",
        "description": "Worker identifier to query"
      },
      "include_state_machine": {"type": "boolean", "default": false},
      "include_path": {"type": "boolean", "default": false}
    },
    "required": ["worker_id"]
  }
}
```

### 4.3 query_resource_points
**描述**: 查询所有资源点状态
```json
{
  "name": "query_resource_points",
  "description": "Get information about all resource points on the map",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_depletion_rate": {"type": "boolean", "default": false},
      "include_worker_assignments": {"type": "boolean", "default": true},
      "min_amount": {
        "type": "integer",
        "minimum": 0,
        "description": "Only return resource points with at least this amount"
      }
    }
  }
}
```

## 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体的响应数据
  },
  "timestamp": "2025-11-03T10:30:00Z",
  "execution_time_ms": 15
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "INVALID_WORKER_ID",
    "message": "Worker with ID 'worker_123' not found",
    "details": {
      "available_workers": ["worker_001", "worker_002"]
    }
  },
  "timestamp": "2025-11-03T10:30:00Z"
}
```

## 实现约束

### 性能要求
- **操作层调用**: 响应时间 < 50ms
- **战术层调用**: 响应时间 < 200ms  
- **战略层调用**: 响应时间 < 500ms
- **查询调用**: 响应时间 < 100ms

### 并发控制
- 支持多个AI Agent同时发送命令
- 命令队列管理，避免冲突
- 状态一致性保证

### 错误处理
- 优雅的错误响应，包含详细错误信息
- 参数验证和类型检查
- 游戏状态验证 (如工人是否存在、是否空闲等)

## 安全考虑

### 权限控制
- AI Agent只能控制属于自己的单位
- 不能查询敌方的详细状态信息
- 命令验证防止无效操作

### 速率限制
- 操作层命令: 最多100次/秒
- 战术层命令: 最多10次/秒
- 战略层命令: 最多1次/秒

## 扩展性设计

### 为未来网络支持预留
- 所有接口设计为异步
- 状态查询与命令执行分离
- 批量操作减少网络往返
- 标准化的错误处理和响应格式