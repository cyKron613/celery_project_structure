#!/bin/bash

# Kubernetes部署脚本
set -e

echo "开始部署Crawl News Center到Kubernetes..."

# 构建Docker镜像
echo "构建Docker镜像..."
docker build -f deploy/Dockerfile -t crawl-news-center:latest .

# 创建所有资源
echo "创建Kubernetes资源..."
kubectl apply -f k8s/deployment.yaml

# 等待服务启动
echo "等待服务启动..."
kubectl wait --for=condition=ready pod -l app=redis --timeout=300s
kubectl wait --for=condition=ready pod -l app=fastapi --timeout=300s

echo "部署完成！"
echo ""
echo "检查服务状态："
kubectl get pods
echo ""
echo "检查服务："
kubectl get services