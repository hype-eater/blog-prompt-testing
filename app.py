import typer

app = typer.Typer(help="A helpful and friendly CLI")


@app.command()
def hello():
    """Say hello"""
    print("Hello")


@app.command()
def intro(name: str = "User"):
    """Reply to an introduction"""
    print(f"Hi, {name}")


if __name__ == '__main__':
    app()