from .d2doc import cli 

def main():
    cli(auto_envvar_prefix='D2DOC')

def run() -> None:
    main()

if __name__ == "__main__":
    main()