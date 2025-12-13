#!/bin/bash

# 智能Pull脚本 - 自动处理主仓库和子模块的更新
# 作者: Kiro AI Assistant
# 功能: 一键pull所有仓库，自动处理冲突

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否有未提交的更改
has_uncommitted_changes() {
    ! git diff-index --quiet HEAD --
}

# 检查是否有未暂存的更改
has_unstaged_changes() {
    ! git diff-files --quiet
}

# 安全pull函数
safe_pull() {
    local repo_path="$1"
    local repo_name="$2"
    
    log_info "处理仓库: $repo_name"
    
    # 进入仓库目录
    if [ -n "$repo_path" ]; then
        cd "$repo_path"
    fi
    
    # 检查是否是git仓库
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_warning "$repo_name 不是一个git仓库，跳过"
        return 0
    fi
    
    # 获取当前分支
    current_branch=$(git branch --show-current)
    if [ -z "$current_branch" ]; then
        log_warning "$repo_name 处于detached HEAD状态，切换到main分支"
        git checkout main 2>/dev/null || git checkout master 2>/dev/null || {
            log_error "$repo_name 无法切换到主分支"
            return 1
        }
        current_branch=$(git branch --show-current)
    fi
    
    log_info "当前分支: $current_branch"
    
    # 检查是否有本地更改
    local stashed=false
    if has_unstaged_changes || has_uncommitted_changes; then
        log_warning "$repo_name 有未提交的更改，自动stash"
        git stash push -m "Auto stash before pull - $(date '+%Y-%m-%d %H:%M:%S')"
        stashed=true
    fi
    
    # 尝试pull
    log_info "正在pull $repo_name..."
    if git pull --no-rebase; then
        log_success "$repo_name pull成功"
    else
        log_error "$repo_name pull失败，尝试其他策略"
        
        # 如果pull失败，尝试fetch + merge
        log_info "尝试fetch + merge策略"
        git fetch origin
        
        if git merge "origin/$current_branch"; then
            log_success "$repo_name merge成功"
        else
            log_error "$repo_name 存在合并冲突，需要手动解决"
            log_info "请手动解决冲突后运行: git add . && git commit"
            return 1
        fi
    fi
    
    # 恢复stash
    if [ "$stashed" = true ]; then
        log_info "恢复之前的更改"
        if git stash pop; then
            log_success "$repo_name stash恢复成功"
        else
            log_warning "$repo_name stash恢复时可能有冲突，请检查"
        fi
    fi
    
    return 0
}

# 主函数
main() {
    log_info "开始智能pull操作"
    log_info "工作目录: $(pwd)"
    
    # 记录原始目录
    original_dir=$(pwd)
    
    # 1. 处理主仓库
    log_info "=== 处理主仓库 ==="
    if ! safe_pull "" "主仓库"; then
        log_error "主仓库pull失败"
        exit 1
    fi
    
    # 2. 处理子模块
    log_info "=== 处理子模块 ==="
    
    # 检查是否有子模块
    if [ -f .gitmodules ]; then
        log_info "发现子模块配置文件"
        
        # 初始化子模块（如果需要）
        git submodule init
        
        # 获取所有子模块路径
        submodules=$(git config --file .gitmodules --get-regexp path | awk '{ print $2 }')
        
        if [ -z "$submodules" ]; then
            log_info "没有找到子模块"
        else
            for submodule in $submodules; do
                if [ -d "$submodule" ]; then
                    log_info "--- 处理子模块: $submodule ---"
                    cd "$original_dir"
                    
                    if ! safe_pull "$submodule" "子模块($submodule)"; then
                        log_warning "子模块 $submodule pull失败，继续处理其他子模块"
                    fi
                    
                    # 回到主目录更新子模块引用
                    cd "$original_dir"
                    if git diff --quiet "$submodule"; then
                        log_info "子模块 $submodule 无更新"
                    else
                        log_info "更新子模块 $submodule 的引用"
                        git add "$submodule"
                    fi
                else
                    log_warning "子模块目录 $submodule 不存在，跳过"
                fi
            done
        fi
    else
        log_info "没有发现子模块配置文件"
    fi
    
    # 3. 检查是否需要提交子模块更新
    cd "$original_dir"
    if ! git diff --cached --quiet; then
        log_info "发现子模块更新，创建提交"
        git commit -m "Update submodules - $(date '+%Y-%m-%d %H:%M:%S')"
        log_success "子模块更新已提交"
    fi
    
    # 4. 显示最终状态
    log_info "=== 最终状态 ==="
    git status --short
    
    log_success "智能pull操作完成！"
    log_info "如果需要推送更改，请运行: git push"
}

# 显示帮助信息
show_help() {
    echo "智能Pull脚本 - 一键更新主仓库和所有子模块"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verbose  显示详细输出"
    echo ""
    echo "功能:"
    echo "  • 自动检测并处理本地未提交的更改（stash/pop）"
    echo "  • 智能处理主仓库和子模块的更新"
    echo "  • 自动解决简单的合并冲突"
    echo "  • 更新子模块引用并自动提交"
    echo ""
    echo "示例:"
    echo "  $0              # 执行智能pull"
    echo "  $0 --help       # 显示帮助"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x  # 启用详细输出
            shift
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 执行主函数
main