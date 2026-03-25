# 🚀 Project: Resilient API Gateway Simulator

## 🎯 Objective

The goal of this project is to design and implement a **resilient API gateway** that interacts with unreliable upstream services (mock vendors) and demonstrates best practices for handling failures in distributed systems.

This project focuses on:

* Handling transient and persistent failures
* Preventing cascading failures
* Ensuring request deduplication (idempotency)
* Improving system observability
* Designing for distributed environments

Instead of integrating real LLM APIs, we simulate multiple unreliable upstream services to isolate and focus on **system reliability patterns**.

---

## 🧩 System Overview

The system consists of two main components:

### 1. Mock Vendor Services

Simulated upstream APIs that intentionally exhibit failure behaviors:

* Random latency
* Rate limiting (HTTP 429)
* Internal errors (HTTP 500)
* Timeouts

Each vendor has different characteristics (e.g., fast but unstable, slow but reliable).

---

### 2. Gateway Service (Main Application)

A FastAPI-based service that:

* Receives client requests
* Routes them to upstream vendors
* Applies resilience patterns:

  * Retry with exponential backoff and jitter
  * Timeout control
  * Circuit breaker
  * Idempotency handling
  * Fallback between vendors
* Exposes observability signals (logs and metrics)

---

## ⚙️ Core Design Goals

* **Resilience**: Gracefully handle upstream failures
* **Isolation**: Prevent one failing dependency from affecting others
* **Correctness**: Avoid duplicate processing via idempotency
* **Observability**: Provide insight into system behavior
* **Scalability Awareness**: Design for distributed deployment

---

# 🧱 Key Features

## 1. Retry with Exponential Backoff and Jitter

* Retries only on transient failures (timeouts, 5xx, 429)
* Uses exponential delay strategy
* Adds jitter to prevent synchronized retry storms

---

## 2. Timeout Strategy

* Separates:

  * Connection timeout
  * Read timeout
* Vendor-specific timeout configuration
* Prevents slow upstream services from blocking the system

---

## 3. Circuit Breaker

* Tracks failure rate per vendor
* Opens circuit after threshold is exceeded
* Temporarily blocks requests to failing vendors
* Allows recovery via half-open state

---

## 4. Idempotency Handling

* Uses idempotency keys to prevent duplicate processing
* First implemented with in-memory store
* Designed to migrate to Redis for distributed environments

---

## 5. Fallback Strategy

* If primary vendor fails:
  → automatically route to secondary vendor
* Ensures higher availability

---

## 6. Observability

### Logging

* Structured logs
* Request ID tracking
* Retry and failure events recorded

### Metrics (`/metrics`)

* Vendor success/failure rate
* Retry count
* Fallback count
* Latency (p50, p95, p99)

---

## 7. (Optional) Bulkhead Isolation

* Vendor-specific concurrency limits
* Prevents one vendor from exhausting shared resources

---

## 8. (Optional) Distributed Lock

* Prevents race conditions when handling the same idempotency key
* Implemented via Redis (`SET NX`)

---

# 🗺️ Development Phases

---

## 🟢 Phase 1 — Core Reliability (MVP)

**Goal:** Build a minimal working system with essential resilience features.

### Scope:

* Mock vendor APIs (2–3 vendors)
* Gateway service with:

  * Retry + exponential backoff + jitter
  * Basic timeout handling
  * Idempotency (in-memory)
  * Fallback between vendors
  * Structured logging

### Outcome:

* Functional system handling unreliable upstream APIs
* Demonstrates core reliability patterns

---

## 🟡 Phase 2 — Failure Isolation & Observability

**Goal:** Improve robustness and production readiness.

### Add:

* Circuit breaker per vendor
* Timeout refinement (connection vs read)
* Metrics endpoint (`/metrics`)
* Vendor-level monitoring:

  * success rate
  * retry count
  * latency

### Outcome:

* System prevents cascading failures
* Observable behavior for debugging and monitoring

---

## 🔵 Phase 3 — Distributed Readiness

**Goal:** Extend system for multi-instance deployment.

### Add:

* Redis-backed idempotency store
* TTL design for idempotency keys
* Distributed lock for race condition handling
* Basic containerization (Docker Compose)

### Outcome:

* System design becomes safe under distributed execution
* Can handle concurrent duplicate requests across instances

---

## 🟣 Phase 4 — Advanced Isolation (Optional)

**Goal:** Simulate production-grade traffic isolation.

### Add:

* Bulkhead pattern:

  * Vendor-specific concurrency limits
  * Separate connection pools (conceptual or simulated)

### Outcome:

* Resource isolation between vendors
* Prevents resource starvation

---

# 🧠 Key Learnings / Interview Talking Points

This project demonstrates:

* Difference between **retry vs circuit breaker**
* Importance of **timeouts to prevent cascading failures**
* Handling **idempotency in distributed systems**
* Designing **fallback strategies for availability**
* Observability via **logs vs metrics**
* Trade-offs in **TTL design for idempotency**
* Strategies for **race condition prevention (distributed lock)**

---

# 💬 Summary

This project is not about building a complex application, but about:

> **Designing a system that remains stable under failure**

It reflects real-world challenges in:

* AI API orchestration
* Microservices communication
* Distributed system reliability

