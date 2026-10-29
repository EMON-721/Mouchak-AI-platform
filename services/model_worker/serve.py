"""Provider-neutral private API entry point. No secret command arguments."""
import os


def configured_port(value=None):
    value = os.getenv("PORT", "8000") if value is None else value
    if not str(value).isascii() or not str(value).isdigit() or not 1 <= int(value) <= 65535:
        raise ValueError("PORT must be an integer from 1 to 65535")
    return int(value)


def main():
    import uvicorn
    uvicorn.run("services.model_worker.main:app", host="0.0.0.0", port=configured_port(), access_log=False)


if __name__ == "__main__":
    main()
