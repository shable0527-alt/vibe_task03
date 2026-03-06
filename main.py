#!/usr/bin/env python3
"""证券知识库生成工具 - 将文档解析、切分、标注后存入向量数据库。"""

import click
from rich.console import Console
from rich.table import Table

from config import Config

console = Console()


@click.group()
def cli():
    """证券知识库生成工具"""
    pass


@cli.command()
@click.argument("input_path")
@click.option("--no-label", is_flag=True, help="跳过 LLM 标注步骤")
@click.option("--chunk-size", type=int, default=None, help="切片 token 大小")
@click.option("--chunk-overlap", type=int, default=None, help="切片重叠 token 数")
def build(input_path: str, no_label: bool, chunk_size: int, chunk_overlap: int):
    """构建知识库：解析文件 -> 切分 -> 标注 -> 存储到向量数据库。

    INPUT_PATH 可以是单个文件或包含文件的目录。
    """
    if chunk_size:
        Config.CHUNK_SIZE = chunk_size
    if chunk_overlap:
        Config.CHUNK_OVERLAP = chunk_overlap

    _check_api_key()

    from pipeline import process_files

    with console.status("[bold green]正在处理文件..."):
        report = process_files(input_path, enable_labeling=not no_label)

    console.print(report.summary())


@cli.command()
@click.argument("query")
@click.option("-k", "--top-k", type=int, default=5, help="返回结果数量")
@click.option("-c", "--category", type=str, default=None, help="按分类过滤")
def search(query: str, top_k: int, category: str):
    """搜索知识库。"""
    _check_api_key()

    from vectorstore import ChromaStore

    store = ChromaStore()
    results = store.search(query, top_k=top_k, filter_category=category)

    if not results:
        console.print("[yellow]未找到相关结果[/yellow]")
        return

    for i, hit in enumerate(results, 1):
        meta = hit["metadata"]
        console.print(f"\n[bold cyan]--- 结果 {i} (相似度: {hit['score']:.3f}) ---[/bold cyan]")
        console.print(f"[dim]来源: {meta.get('source_file', '?')} | "
                      f"页码: {meta.get('page_number', '?')} | "
                      f"分类: {meta.get('category', '?')}[/dim]")
        if meta.get("summary"):
            console.print(f"[green]摘要: {meta['summary']}[/green]")
        if meta.get("keywords"):
            console.print(f"[blue]关键词: {meta['keywords']}[/blue]")
        console.print(hit["text"][:500])


@cli.command()
def stats():
    """查看知识库统计信息。"""
    from vectorstore import ChromaStore

    store = ChromaStore()
    info = store.get_stats()

    table = Table(title="知识库统计")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    table.add_row("集合名称", info["collection_name"])
    table.add_row("文档总数", str(info["total_documents"]))
    console.print(table)


@cli.command()
@click.argument("source_file")
def delete(source_file: str):
    """删除指定来源文件的所有知识库条目。"""
    from vectorstore import ChromaStore

    store = ChromaStore()
    count = store.delete_by_source(source_file)
    console.print(f"已删除 [bold]{count}[/bold] 条来自 '{source_file}' 的记录")


@cli.command()
@click.argument("input_path")
def preview(input_path: str):
    """预览文件解析和切分结果（不进行标注和存储）。"""
    from parsers import parse_file
    from parsers.router import get_all_files
    from chunkers import chunk_document

    files = get_all_files(input_path)
    if not files:
        console.print("[yellow]未找到支持的文件[/yellow]")
        return

    for fpath in files:
        console.print(f"\n[bold]{'='*60}[/bold]")
        console.print(f"[bold cyan]文件: {fpath}[/bold cyan]")

        try:
            doc = parse_file(fpath)
            console.print(f"类型: {doc.file_type} | 页数: {len(doc.pages)}")

            chunks = chunk_document(doc)
            console.print(f"切片数: {len(chunks)}")

            for i, chunk in enumerate(chunks[:3]):
                console.print(f"\n[dim]--- 切片 {i + 1}/{len(chunks)} ---[/dim]")
                console.print(chunk.text[:300])
                if len(chunk.text) > 300:
                    console.print("[dim]...(截断)[/dim]")

            if len(chunks) > 3:
                console.print(f"\n[dim]... 还有 {len(chunks) - 3} 个切片未显示[/dim]")
        except Exception as e:
            console.print(f"[red]解析失败: {e}[/red]")


@cli.command()
@click.option("-p", "--port", type=int, default=8000, help="服务端口")
@click.option("-h", "--host", type=str, default="0.0.0.0", help="监听地址")
def serve(port: int, host: str):
    """启动 AI 客服 Web 服务。"""
    _check_api_key()

    import uvicorn

    console.print(f"[bold green]AI 客服服务启动中...[/bold green]")
    console.print(f"  Web 界面:  http://localhost:{port}")
    console.print(f"  API 接口:  http://localhost:{port}/api/chat")
    console.print(f"  API 文档:  http://localhost:{port}/docs")
    uvicorn.run("server:app", host=host, port=port, reload=False)


def _check_api_key():
    if not Config.OPENAI_API_KEY:
        console.print(
            "[red]错误: 未设置 OPENAI_API_KEY。\n"
            "请在 .env 文件中设置或通过环境变量设置。[/red]"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
