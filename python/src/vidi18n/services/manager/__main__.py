from uvicorn import run


def main():
    run("vidi18n.services.manager:app", host="0.0.0.0", port=8081, reload=True)


if __name__ == "__main__":
    main()
