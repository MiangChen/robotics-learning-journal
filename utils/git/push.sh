#!/bin/bash

# 一键推送脚本（支持 submodule）

MESSAGE=${1:-"update"}

echo "=== 推送 docs 子仓库 ==="
cd docs
git add -A
git commit -m "$MESSAGE" || echo "docs: 无变更"
git push
cd ..

echo ""
echo "=== 推送主仓库 ==="
git add -A
git commit -m "$MESSAGE" || echo "主仓库: 无变更"
git push

echo ""
echo "=== 完成 ==="
