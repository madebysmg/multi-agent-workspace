# 비용 최적화 전략

> A2A 분산 시스템 비용 절감 설계 및 단계별 확장 전략

**작성일**: 2025-10-22
**목표**: 월 $5,222 → $500-1,500 (70-90% 절감)

---

## 📋 목차

1. [현재 비용 분석](#현재-비용-분석)
2. [비용 절감 전략](#비용-절감-전략)
3. [단계별 확장 계획](#단계별-확장-계획)
4. [하이브리드 아키텍처](#하이브리드-아키텍처)
5. [실행 계획](#실행-계획)

---

## 현재 비용 분석

### 풀스케일 프로덕션 비용 (월간)

| 리소스 | 사양 | 수량 | 월 비용 | 비중 |
|--------|------|------|---------|------|
| **Research (ECS Fargate)** | 8vCPU, 16GB | 10 | $3,528 | **67.6%** ⚠️ |
| Extraction (ECS Fargate) | 4vCPU, 8GB | 5 | $864 | 16.5% |
| Reflection (ECS Fargate) | 2vCPU, 4GB | 2 | $172 | 3.3% |
| Coordinator (ECS Fargate) | 2vCPU, 4GB | 1 | $86 | 1.6% |
| RDS PostgreSQL | db.t3.large × 2 | 2 | $208 | 4.0% |
| ElastiCache Redis | cache.t3.medium | 2 | $98 | 1.9% |
| NAT Gateway | - | 2 | $64 | 1.2% |
| ALB + S3 + 기타 | - | - | $202 | 3.9% |
| **총계** | | | **$5,222** | **100%** |

**핵심 문제**:
- Research Agent가 **67.6%** 차지 → 최우선 절감 대상
- 24/7 풀가동 가정 → 실제 사용률 고려 필요

---

## 비용 절감 전략

### 전략 1: 단계별 확장 (Phased Scaling) ⭐⭐⭐

**개념**: 초기에는 최소 인스턴스로 시작, 수요에 따라 확장

#### Phase 0: PoC/개발 환경 ($200/월)

```yaml
리소스 구성:
- Research Agent: 1개 (t3.large: 2vCPU, 8GB)
- Extraction Agent: 1개 (t3.medium: 2vCPU, 4GB)
- Reflection Agent: 1개 (t3.small: 2vCPU, 2GB)
- Coordinator: 1개 (t3.small: 2vCPU, 2GB)
- RDS PostgreSQL: db.t3.micro (1개, 복제 없음)
- Redis: cache.t3.micro (1개)
- NAT Gateway: 1개
```

**비용**:
```
ECS Fargate:
- Research (2vCPU, 8GB): $0.12/h × 720h = $86
- Extraction (2vCPU, 4GB): $0.12/h × 720h = $86
- Reflection (2vCPU, 2GB): $0.06/h × 720h = $43
- Coordinator (2vCPU, 2GB): $0.06/h × 720h = $43

RDS: db.t3.micro = $13
Redis: cache.t3.micro = $13
NAT: 1개 = $32
ALB + S3 = $50

총 비용: ~$366/월
```

**처리 능력**: ~5-10 companies/hour (순차 처리)

---

#### Phase 0 대안: 무료 티어 Redis 서비스 ($0/월) ⭐ NEW

**개념**: 초기 PoC/개발 단계에서는 무료 SaaS Redis 서비스 활용

무료 티어를 제공하는 주요 Redis 클라우드 서비스:

##### 1. Upstash Redis (추천) ⭐⭐⭐

```yaml
스펙:
  - Storage: 256 MB
  - Commands: 500K/월
  - Bandwidth: 10 GB/월
  - Performance: 10K commands/sec
  - Connections: 10,000 동시 연결
  - Request Size: 최대 10MB
  - Record Size: 최대 100MB

특징:
  - ✅ Serverless 아키텍처
  - ✅ 글로벌 복제 지원
  - ✅ REST API 제공
  - ✅ 프로덕션 사용 가능
  - ✅ 무제한 기간

비용: $0/월 (영구 무료)
```

**사용 사례**: 프로토타입, 취미 프로젝트, 초기 MVP

**통합 예시**:
```python
# coordinator/cache.py
import os
from upstash_redis import Redis

redis_client = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

# 사용법은 일반 Redis와 동일
await redis_client.set("key", "value")
result = await redis_client.get("key")
```

---

##### 2. Redis Cloud (공식)

```yaml
스펙 (30MB Free Plan):
  - Storage: 30 MB
  - Connections: 30 동시 연결
  - Bandwidth: 5 GB/월
  - Throughput: 100 ops/sec
  - CIDR Rules: 1개

특징:
  - ✅ 공식 Redis 서비스
  - ✅ 학습 및 테스트 최적화
  - ✅ 프로토타입 개발용
  - ✅ 무제한 기간
  - ⚠️ 프로덕션 사용 제한적

비용: $0/월 (영구 무료)
```

**사용 사례**: Redis 학습, 간단한 테스트

---

##### 3. Aiven for Valkey

```yaml
스펙:
  - RAM: 1 GB
  - CPU: 1 vCPU
  - Dedicated VM: 1개
  - Cloud: AWS (선택 리전)
  - Backups: 포함
  - Monitoring: 성능 그래프 포함

특징:
  - ✅ 가장 큰 무료 리소스 (1GB RAM)
  - ✅ 전용 VM 제공
  - ✅ 자동 백업
  - ✅ 모니터링 대시보드
  - ✅ Terraform 지원
  - ⚠️ 비활동 시 자동 종료

비용: $0/월 (영구 무료, 활성 사용 시)
```

**사용 사례**: 개발/스테이징 환경, 소규모 프로덕션

**주의사항**:
- 장기간 미사용 시 자동 종료 (이메일 사전 통지)
- 재시작 간단

---

##### 4. Render Redis

```yaml
스펙:
  - Storage: 25 MB
  - Connections: 제한 있음
  - 특징: Zero DevOps

비용: $0/월
```

**사용 사례**: Render 플랫폼 사용자

---

#### 무료 티어 비교표

| 서비스 | 스토리지 | Commands/월 | Bandwidth | 추천도 |
|--------|----------|-------------|-----------|--------|
| **Upstash** ⭐ | 256 MB | 500K | 10 GB | ⭐⭐⭐ 최고 |
| **Aiven** | 1 GB RAM | 무제한 | 포함 | ⭐⭐⭐ 개발용 최적 |
| **Redis Cloud** | 30 MB | ~260K (100 ops/s) | 5 GB | ⭐⭐ 학습용 |
| **Render** | 25 MB | - | - | ⭐ Render 사용자 |

---

#### Phase 0 최적화 비용 (무료 Redis 적용)

**원래 구성**:
```
ECS Fargate: $258
RDS: $13
Redis: $13  ← ElastiCache
NAT: $32
ALB + S3: $50
───────────
총: $366/월
```

**무료 Redis 적용**:
```
ECS Fargate: $258
RDS: $13
Redis: $0  ← Upstash/Aiven 무료 티어
NAT: $32
ALB + S3: $50
───────────
총: $353/월 (4% 절감)
```

**추가 최적화** (VPC Endpoint + 무료 Redis):
```
ECS Fargate: $258
RDS: $13
Redis: $0  ← 무료 티어
NAT: $0    ← VPC Endpoint로 대체
ALB + S3: $50
───────────
총: $321/월 (12% 절감)
```

---

#### 무료 Redis 사용 시 고려사항

**장점** ✅:
- 초기 비용 절감 ($13/월 → $0)
- 빠른 시작 (설정 5분)
- 관리 부담 없음
- Phase 1 전환 전까지 충분

**제약사항** ⚠️:
- 스토리지 제한 (30-256 MB)
- 처리량 제한 (100-10K ops/sec)
- 프로덕션 확장 시 유료 전환 필요

**권장 마이그레이션 경로**:
```
Phase 0: Upstash 무료 (256MB)
    ↓ (트래픽 증가)
Phase 1: ElastiCache t3.small ($28/월)
    ↓ (대규모 처리)
Phase 2+: ElastiCache t3.medium+ ($50+/월)
```

---

#### Phase 1: 스타트업 환경 ($500-800/월)

```yaml
리소스 구성:
- Research Agent: 3개 (c5.large: 2vCPU, 4GB)  ← Compute Optimized
- Extraction Agent: 2개 (t3.medium)
- Reflection Agent: 1개 (t3.small)
- Coordinator: 1개 (t3.medium)
- RDS PostgreSQL: db.t3.small (Primary + Replica)
- Redis: cache.t3.small (1개)
- Spot Instances 활용
```

**비용** (Spot 70% 할인 적용):
```
ECS Fargate Spot:
- Research (2vCPU, 4GB) × 3: $0.04/h × 3 × 720h = $86 (Spot)
- Extraction × 2: $0.04/h × 2 × 720h = $58 (Spot)
- Reflection × 1: $0.02/h × 720h = $14 (Spot)
- Coordinator × 1: $0.04/h × 720h = $29

RDS: db.t3.small × 2 = $52
Redis: cache.t3.small = $28
NAT: 1개 = $32
ALB + S3 = $50

총 비용: ~$349/월 (Spot 기준)
        ~$650/월 (On-Demand 혼합)
```

**처리 능력**: ~30-50 companies/hour (병렬 3개)

---

#### Phase 2: 성장 단계 ($1,200-1,500/월)

```yaml
리소스 구성:
- Research Agent: 5개 (c5.xlarge: 4vCPU, 8GB) + Spot
- Extraction Agent: 3개 (t3.medium) + Spot
- Reflection Agent: 2개 (t3.small)
- Coordinator: 1개 (t3.large)
- RDS: db.t3.medium (Primary + Replica)
- Redis: cache.t3.medium (Cluster)
- Reserved Instances (1년 약정)
```

**비용** (Reserved 40% 할인 + Spot 혼합):
```
ECS Fargate (Reserved + Spot):
- Research × 5: ~$400
- Extraction × 3: ~$180
- Reflection × 2: ~$60
- Coordinator × 1: ~$50

RDS (Reserved): db.t3.medium × 2 = $80
Redis (Reserved): cache.t3.medium = $50
NAT: 2개 = $64
ALB + S3 + Data Transfer = $150

총 비용: ~$1,034/월 (Reserved)
        ~$1,400/월 (Spot 혼합)
```

**처리 능력**: ~150-200 companies/hour

---

### 전략 2: Spot Instances 적극 활용 ⭐⭐⭐

**ECS Fargate Spot**: 최대 70% 할인

```hcl
# terraform/ecs_spot.tf
resource "aws_ecs_service" "research_agent_spot" {
  name            = "research-agent-spot"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.research_agent.arn
  desired_count   = 3

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }

  # Graceful handling of interruptions
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }
}
```

**장점**:
- ✅ 70% 비용 절감
- ✅ 중단 시 자동 재시작

**주의**:
- ⚠️ 2분 사전 통지 후 중단 가능
- ⚠️ Critical 작업은 On-Demand 사용

**권장 비율**:
```
Research Agent:
- FARGATE_SPOT: 70% (배치 처리)
- FARGATE: 30% (실시간 요청)

Extraction/Reflection: 100% Spot (짧은 작업)
Coordinator: 100% On-Demand (중요)
```

---

### 전략 3: Reserved Instances (1년/3년 약정) ⭐⭐

**할인율**:
- 1년 약정: ~40% 할인
- 3년 약정: ~60% 할인

**적용 대상**:
- RDS PostgreSQL (안정적 부하)
- ElastiCache Redis
- 기본 인스턴스 (Coordinator, 최소 Research)

**계산 예시**:
```
RDS db.t3.medium On-Demand: $104/월
RDS db.t3.medium Reserved (1년): $62/월 (40% 절감)
RDS db.t3.medium Reserved (3년): $42/월 (60% 절감)
```

---

### 전략 4: Auto-Scaling 공격적 설정 ⭐⭐

**현재 (항상 10개)**:
```yaml
Research Agent: 10개 (24/7)
월 비용: $3,528
```

**최적화 (수요 기반)**:
```yaml
최소: 2개 (야간/주말)
평균: 5개 (평일)
최대: 10개 (피크 시간)

평균 인스턴스: ~4개
월 비용: ~$1,411 (60% 절감)
```

**Auto-Scaling 정책**:
```hcl
resource "aws_appautoscaling_policy" "research_agent_cpu" {
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 60  # ← 70에서 60으로 낮춤 (더 빠른 스케일)
    scale_in_cooldown  = 180  # ← 300에서 180으로 (더 빠른 스케일 다운)
    scale_out_cooldown = 30   # ← 60에서 30으로 (더 빠른 스케일 업)
  }
}

# 시간대별 스케줄링
resource "aws_appautoscaling_scheduled_action" "scale_down_night" {
  name               = "scale-down-night"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.research_agent.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 22 * * ? *)"  # 오후 10시

  scalable_target_action {
    min_capacity = 1
    max_capacity = 3
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_up_morning" {
  name               = "scale-up-morning"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.research_agent.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 8 * * ? *)"  # 오전 8시

  scalable_target_action {
    min_capacity = 3
    max_capacity = 10
  }
}
```

---

### 전략 5: Serverless 하이브리드 ⭐⭐

**개념**: 비용-효율 작업은 Lambda로

```
┌─────────────────────────────────────────┐
│          API Gateway                     │
└──────┬──────────────┬───────────────────┘
       │              │
       ↓              ↓
┌─────────────┐  ┌─────────────┐
│  Lambda     │  │  ECS Fargate│
│  (간단 조회)  │  │  (복잡 처리) │
└─────────────┘  └─────────────┘
```

**Lambda 적용 대상**:
- Reflection Agent (가벼운 작업)
- 캐시 조회 (DB에서 기존 데이터 반환)
- Health check

**비용 비교**:
```
Reflection Agent (ECS Fargate):
- 2vCPU, 4GB × 2개 = $172/월

Reflection Agent (Lambda):
- 2GB, 평균 10초 실행
- 10,000 호출/월
- 비용: ~$5/월

절감: $167/월 (97%)
```

**Lambda 구현**:
```python
# lambda/reflection_handler.py
import json

def lambda_handler(event, context):
    # A2A task 파싱
    task = json.loads(event['body'])
    input_data = extract_input(task)

    # Reflection 로직 (기존 코드 재사용)
    from src.agents.company_research.reflection import reflection_node

    result = reflection_node({
        "extracted_data": input_data["extracted_data"],
        "extraction_schema": input_data["schema"]
    }, Configuration())

    # A2A 응답
    return {
        'statusCode': 200,
        'body': json.dumps(create_a2a_response(result))
    }
```

---

### 전략 6: 데이터베이스 최적화 ⭐⭐

#### 6.1 RDS Aurora Serverless v2

```yaml
현재: RDS PostgreSQL db.t3.large × 2 = $208/월

대안: Aurora Serverless v2
- 최소: 0.5 ACU (1GB RAM)
- 최대: 8 ACU (16GB RAM)
- 평균: 2 ACU (4GB RAM)
- 비용: ~$87/월 (58% 절감)
```

**장점**:
- ✅ 자동 스케일링 (0.5 ~ 최대 ACU)
- ✅ 사용한 만큼만 과금
- ✅ 완전 관리형

**Terraform**:
```hcl
resource "aws_rds_cluster" "aurora_serverless" {
  cluster_identifier      = "company-research-aurora"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4"
  database_name           = "companyresearch"
  master_username         = "admin"
  master_password         = random_password.db_password.result

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 8
  }
}

resource "aws_rds_cluster_instance" "aurora_serverless_instance" {
  cluster_identifier = aws_rds_cluster.aurora_serverless.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora_serverless.engine
  engine_version     = aws_rds_cluster.aurora_serverless.engine_version
}
```

#### 6.2 Connection Pooling (PgBouncer)

```
현재: 각 Agent가 직접 연결 (100+ connections)
문제: Connection 오버헤드

해결: PgBouncer
- Connection pooling
- 최대 10-20 실제 연결
- Lambda에서 효과적
```

---

### 전략 7: 캐싱 전략 강화 ⭐⭐⭐

**Redis 캐싱으로 API 비용 절감**

```python
# coordinator/cache.py
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    decode_responses=True
)

async def research_with_cache(company_name, schema):
    # Cache key
    cache_key = f"research:{company_name}:{hash(json.dumps(schema))}"

    # 캐시 확인 (30일)
    cached = redis_client.get(cache_key)
    if cached:
        print(f"✅ Cache HIT: {company_name}")
        return json.loads(cached)

    # Cache MISS → 실제 조사
    print(f"❌ Cache MISS: {company_name}")
    result = await process_company(company_name, schema)

    # 캐시 저장 (30일)
    redis_client.setex(
        cache_key,
        timedelta(days=30),
        json.dumps(result)
    )

    return result
```

**절감 효과**:
```
1,000개 회사 조사:
- 초회: 1,000번 API 호출
- 2차: 900번 캐시 HIT, 100번만 API 호출 (90% 절감)

API 비용 (Claude + Tavily):
- 초회: $400
- 2차: $40 (90% 절감)
```

---

### 전략 8: NAT Gateway 제거 ⭐

**현재**: NAT Gateway × 2 = $64/월

**대안 1**: VPC Endpoints (추천)
```hcl
# S3 VPC Endpoint (무료)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = aws_route_table.private_app[*].id
}

# DynamoDB VPC Endpoint (무료)
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
}

절감: $64/월 → $0/월
```

**대안 2**: Public Subnet에 배포 (보안 고려)
```yaml
장점: NAT 불필요
단점: 보안 약화 (비추천)
```

---

## 단계별 확장 계획

### Phase 0: PoC/개발 ($200-400/월)

**목표**: 기술 검증 및 프로토타입

**구성**:
```yaml
Compute:
  - Research: 1개 (t3.large)
  - Extraction: 1개 (t3.medium)
  - Reflection: Lambda (Serverless)
  - Coordinator: 1개 (t3.small)

Database:
  - RDS: db.t3.micro (복제 없음)
  - Redis: cache.t3.micro

Network:
  - NAT: 1개 (또는 VPC Endpoint)
  - ALB: 기본
```

**처리 능력**: 5-10 companies/hour
**예상 비용**: $200-400/월

---

### Phase 1: 스타트업 ($500-800/월)

**목표**: 실제 서비스 런칭

**구성**:
```yaml
Compute (Fargate Spot 70%):
  - Research: 3개 (c5.large Spot)
  - Extraction: 2개 (t3.medium Spot)
  - Reflection: Lambda
  - Coordinator: 1개 (t3.medium)

Database:
  - Aurora Serverless v2 (0.5-4 ACU)
  - Redis: cache.t3.small

Optimization:
  - VPC Endpoints (S3, DynamoDB)
  - Aggressive auto-scaling
  - Cache hit rate 50%+
```

**처리 능력**: 30-50 companies/hour
**예상 비용**: $500-800/월

---

### Phase 2: 성장 ($1,200-1,500/월)

**목표**: 대량 처리 및 안정성

**구성**:
```yaml
Compute (Reserved 30% + Spot 50%):
  - Research: 5개 (c5.xlarge, Reserved + Spot)
  - Extraction: 3개 (t3.medium Spot)
  - Reflection: Lambda + 1 ECS (백업)
  - Coordinator: 1개 (t3.large Reserved)

Database:
  - Aurora Serverless v2 (1-8 ACU)
  - Redis: cache.t3.medium Cluster

Optimization:
  - Reserved Instances (1년)
  - Cache hit rate 70%+
  - Time-based scaling
```

**처리 능력**: 150-200 companies/hour
**예상 비용**: $1,200-1,500/월

---

### Phase 3: 엔터프라이즈 ($3,000-5,000/월)

**목표**: 대규모 트래픽 및 HA

**구성**:
```yaml
Compute (Reserved 50% + Spot 30%):
  - Research: 10개 (c5.2xlarge)
  - Extraction: 5개 (c5.xlarge)
  - Reflection: 2개 (t3.medium)
  - Coordinator: 2개 (HA)

Database:
  - Aurora Serverless v2 (2-16 ACU) + Replica
  - Redis: cache.r5.large Cluster

Optimization:
  - Reserved Instances (3년)
  - Multi-region (DR)
  - Cache hit rate 85%+
```

**처리 능력**: 400-800 companies/hour
**예상 비용**: $3,000-5,000/월

---

## 하이브리드 아키텍처 (권장)

### 최적 비용-성능 조합

```
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
       ↓              ↓              ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Lambda     │ │ ECS Fargate │ │ ECS Fargate │
│             │ │   Spot      │ │  On-Demand  │
│ - 캐시 조회  │ │ - 배치 처리 │ │ - 실시간    │
│ - Reflection│ │ - Research  │ │ - Critical  │
│ - Health    │ │ - Extract   │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
       │              │              │
       └──────────────┴──────────────┘
                      ↓
          ┌───────────────────────┐
          │ Aurora Serverless v2  │
          │ + Redis (t3.small)    │
          └───────────────────────┘
```

**비율**:
- Lambda: 40% (가벼운 작업, 캐시)
- Fargate Spot: 50% (배치 처리)
- Fargate On-Demand: 10% (실시간, Critical)

**예상 비용** (Phase 1):
```
Lambda (Reflection, Cache): $20
Fargate Spot (Research × 3, Extract × 2): $144
Fargate On-Demand (Coordinator, 1 Research): $115
Aurora Serverless v2: $87
Redis: $28
VPC Endpoints: $0
ALB + S3: $70

총: ~$464/월 (91% 절감!)
```

---

## 실행 계획

### 즉시 적용 가능 (1주)

1. **VPC Endpoints 추가** → NAT Gateway 제거
   - 절감: $64/월
   - 작업: Terraform 1시간

2. **Reflection을 Lambda로 전환**
   - 절감: $167/월
   - 작업: 2-3일

3. **Auto-Scaling 공격적 설정**
   - 절감: ~$1,500/월
   - 작업: 1일

**즉시 절감**: ~$1,731/월 (33%)

---

### 단기 적용 (2-4주)

4. **Aurora Serverless v2로 마이그레이션**
   - 절감: $121/월
   - 작업: 1주 (마이그레이션 포함)

5. **Fargate Spot 전략 도입**
   - 절감: ~$1,500/월
   - 작업: 1주

6. **캐싱 전략 강화**
   - 절감: API 비용 50-70%
   - 작업: 1주

**단기 절감**: ~$3,121/월 (60%)

---

### 중기 적용 (2-3개월)

7. **Reserved Instances 구매 (1년)**
   - 절감: ~$500/월
   - 작업: 계획 수립

8. **Phase별 확장 전략 실행**
   - Phase 0 → Phase 1 → Phase 2
   - 수요에 맞춰 점진적 확장

**최종 비용 (Phase 1)**:
```
기존: $5,222/월
최적화: $500-800/월
절감: $4,422-4,722/월 (85-90% 절감!)
```

---

## 비용 비교 요약

| 단계 | 월 비용 | 처리량 | 회사당 비용 | 절감율 |
|------|---------|--------|-------------|--------|
| **풀스케일 (기존)** | $5,222 | 400/h | $0.0176 | - |
| **Phase 0 (PoC)** | $366 | 10/h | $0.0508 | 93% ⬇️ |
| **Phase 1 (최적화)** | $464 | 50/h | $0.0129 | **91% ⬇️** ⭐ |
| **Phase 2 (성장)** | $1,400 | 200/h | $0.0097 | 73% ⬇️ |
| **Phase 3 (엔터프라이즈)** | $3,800 | 800/h | $0.0066 | 27% ⬇️ |

**권장**: Phase 1에서 시작 → 수요에 따라 Phase 2로 확장

---

## 결론

### 최적 전략

1. ✅ **Phase 1 하이브리드로 시작** ($464/월)
   - Lambda (Reflection, Cache)
   - Fargate Spot (Research, Extraction)
   - Aurora Serverless v2
   - VPC Endpoints

2. ✅ **공격적 Auto-Scaling**
   - 시간대별 스케줄링
   - CPU 60% target

3. ✅ **캐싱 극대화**
   - Redis 30일 캐시
   - 90% cache hit 목표

4. ✅ **점진적 확장**
   - 수요 증가 시 Phase 2로
   - Reserved Instances 활용

**최종 절감**: $5,222 → $464 (**91% 절감, $4,758/월 절약**)

---

**작성**: 2025-10-22
**다음 검토**: 월간 사용량 분석 후 최적화
