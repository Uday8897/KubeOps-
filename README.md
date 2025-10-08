KubeOps AI: Autonomous Kubernetes Cost Optimization Agent
KubeOps AI is a production-grade, autonomous agent that leverages AI to analyze, monitor, and optimize Kubernetes cluster costs. It combines the analytical power of Large Language Models with the expert recommendations of Kubecost to find and safely execute cost-saving actions, all managed through a modern Human-in-the-Loop (HITL) dashboard.
<img width="1482" height="856" alt="image" src="https://github.com/user-attachments/assets/f842d32c-d54c-4a18-9d24-b5ef5d1afe84" />

<img width="1438" height="373" alt="image" src="https://github.com/user-attachments/assets/00a4abd1-31a9-43f7-bae2-5fa2c8421255" />
<img width="1513" height="812" alt="image" src="https://github.com/user-attachments/assets/97d651f2-0003-4af1-959d-9afe5b3a7e92" />




The Problem
Kubernetes is powerful, but its dynamic and shared nature often leads to significant financial waste from:

Over-provisioned workloads with excessive CPU/memory requests.

Idle or abandoned resources like old pods and unused storage volumes (PVCs).

Inefficient cluster scaling and underutilized nodes.

Answering the simple question, "Where is my money going?" becomes a complex engineering challenge.

The Solution: KubeOps AI
KubeOps AI solves this problem by creating a closed-loop, intelligent system:

Monitor: It uses Kubecost and Prometheus to get a real-time, accurate picture of your cluster's spending and resource utilization.

Analyze: It feeds this data to a Large Language Model (powered by Groq) to generate high-level insights and queries expert systems like Kubecost for specific, data-driven savings recommendations.

Act: It converts these recommendations into concrete actions, validates them against a robust safety controller, and either executes them autonomously (for high-confidence, non-destructive tasks) or queues them for human approval in a sleek React dashboard.

Core Features
Autonomous Optimization: Automatically acts on expert recommendations from Kubecost for tasks like workload rightsizing.

Intelligent Analysis: Uses a Groq-powered LLM (Llama 3) to analyze cluster state and provide contextual insights.

Human-in-the-Loop (HITL) Dashboard: A modern React UI for approving or rejecting sensitive or destructive actions, ensuring a human is always in control.

Selective Autonomy: High-confidence, non-destructive actions are executed automatically, while all destructive actions (deletions, node drains) require manual approval.

Real-time Cost Monitoring: Integrates directly with Kubecost to track real-time spending and measure the financial impact of its actions.

Comprehensive Tooling: Includes a suite of tools for:

Workload Rightsizing: Based on Kubecost's historical analysis.

Node Optimization: Identifies underutilized nodes for consolidation.

Resource Cleanup: Cleans up completed pods and abandoned PVCs.

Production-Ready Architecture: Built with FastAPI and Docker, ready for cloud deployment. State is managed in-memory for simplicity.

Technology Stack
Backend: Python, FastAPI, LangGraph, LangChain, Pydantic

AI Core: Groq API (Llama 3)

Frontend: React, Tailwind CSS, React Router

Cluster Services: Kubernetes, Prometheus, Kubecost, Helm

Containerization: Docker

Getting Started: Local Development Setup
This guide will help you run the entire system on your local machine using Docker Desktop.

Prerequisites
Docker Desktop (with Kubernetes enabled and resources increased: 8GB+ Memory, 4+ CPUs recommended)

kubectl configured to point to docker-desktop.

Helm (the Kubernetes package manager)

Node.js and npm for the frontend.

Python and pip for the backend.

1. Set Up Cluster Services (Prometheus & Kubecost)
Install the monitoring stack into your local Docker Desktop cluster using Helm.

# Install Prometheus
helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

# Install Kubecost
helm repo add kubecost [https://kubecost.github.io/cost-analyzer/](https://kubecost.github.io/cost-analyzer/)
helm repo update
helm install kubecost kubecost/cost-analyzer --namespace kubecost --create-namespace

2. Set Up the Backend
Configure Environment: Copy .env.example to .env and fill in your GROQ_API_KEY. The default URLs for Prometheus and Kubecost are already set for the port-forwarding step.

cp .env.example .env

Install Dependencies: Create a virtual environment and install the Python packages.

python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

Start Port-Forwards: Open two separate terminals and run these commands. Keep them running.

# Terminal 1: Prometheus
kubectl port-forward --namespace monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Terminal 2: Kubecost
kubectl port-forward --namespace kubecost service/kubecost-cost-analyzer 9000:9090

Run the Backend Server: In a new terminal, activate your virtual environment and start the FastAPI app.

uvicorn k8s_cost_optimizer.main:app --reload

The backend is now running on http://localhost:8000.

3. Set Up the Frontend
Navigate to the UI directory:

cd k8s-optimizer-ui

Install Dependencies:

npm install

Run the Frontend:

npm start

Your browser will open to http://localhost:3000, where you can see the dashboard.

Usage
Dashboard: View real-time savings, pending actions, and recent activity.

Run New Analysis: Click this button to trigger the agent. It will analyze the cluster and populate the "Action Approval" section.

Approve/Reject: Review each pending action and its estimated savings, then approve or reject it.

Reports Page: View a detailed history of all past analysis runs, including the AI summary and every action that was generated.

Deploying to the Cloud
This project is ready for cloud deployment.

Build and Push the Docker Image:

docker build -t your-repo/k8s-optimizer-agent:v1.0 .
docker push your-repo/k8s-optimizer-agent:v1.0

Update kubernetes_manifests.yaml: Change the image: field to point to the image you just pushed.

Apply to your Cloud Cluster:

kubectl apply -f kubernetes_manifests.yaml
